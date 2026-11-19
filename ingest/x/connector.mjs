// Line of Blue: X (Twitter) recent-search connector.
// Narrative-first: it runs approved keyword sets only, never looks up or follows accounts,
// and pseudonymises every author before anything is stored. Spending is capped before each
// request, so a run can never read more posts than the daily and monthly caps allow.
import { createHmac } from 'node:crypto';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname } from 'node:path';

export const API = 'https://api.x.com/2/tweets/search/recent';
export const FIELDS = 'created_at,lang,public_metrics,author_id';

export class CapError extends Error {}
export class ApiError extends Error { constructor(msg, status) { super(msg); this.status = status; } }

// ------------------------------------------------------------------ budget
// The ledger counts posts read (X bills per post returned). Before a request we reserve the
// maximum the request could return; if that would cross a cap, the request is not sent.
export class Budget {
  constructor({ file, dailyCap, monthlyCap, pricePerPost, now = () => new Date() }) {
    Object.assign(this, { file, dailyCap, monthlyCap, pricePerPost, now });
    this.ledger = existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : { days: {}, months: {} };
  }
  keys() { const d = this.now().toISOString(); return [d.slice(0, 10), d.slice(0, 7)]; }
  used() { const [day, month] = this.keys(); return { day: this.ledger.days[day] || 0, month: this.ledger.months[month] || 0 }; }
  remaining() { const u = this.used(); return Math.max(0, Math.min(this.dailyCap - u.day, this.monthlyCap - u.month)); }
  // largest request size allowed now (X needs 10..100); 0 means stop
  allowance(want) { const r = Math.min(want, this.remaining()); return r >= 10 ? r : 0; }
  record(n) {
    const [day, month] = this.keys();
    this.ledger.days[day] = (this.ledger.days[day] || 0) + n;
    this.ledger.months[month] = (this.ledger.months[month] || 0) + n;
    mkdirSync(dirname(this.file), { recursive: true });
    writeFileSync(this.file, JSON.stringify(this.ledger, null, 1));
  }
  summary() { const u = this.used(); return { readToday: u.day, readThisMonth: u.month, dailyCap: this.dailyCap, monthlyCap: this.monthlyCap, estimatedSpendThisMonthUSD: +(u.month * this.pricePerPost).toFixed(2), monthlyCapUSD: +(this.monthlyCap * this.pricePerPost).toFixed(2) }; }
}

// ------------------------------------------------------------------ privacy
export function pseudonym(authorId, salt) {
  if (!salt || salt.length < 16) throw new Error('X_PSEUDONYM_SALT must be set (16+ characters) before any live run.');
  return 'acct_' + createHmac('sha256', salt).update(String(authorId)).digest('hex').slice(0, 10);
}
// remove handles and links to people's profiles; keep the words
export const scrub = (text) => String(text).replace(/@\w{1,15}/g, '@user').replace(/https?:\/\/(x|twitter)\.com\/\w+(\/status\/\d+)?/gi, '[link]');

// map one API post to the demo's post shape
export function toPost(tw, set, salt) {
  const m = tw.public_metrics || {};
  return {
    id: 'X' + createHmac('sha256', salt).update(String(tw.id)).digest('hex').slice(0, 12),
    narrative: null, set: set.id, platform: 'x', source: 'x-recent-search', synthetic: false,
    t: tw.created_at, account: pseudonym(tw.author_id, salt), place: null,
    text: scrub(tw.text), lang: tw.lang || 'und',
    reach: m.impression_count ?? 0, shares: (m.retweet_count || 0) + (m.quote_count || 0), flags: [],
  };
}

// ------------------------------------------------------------------ sets
export function loadSets(file) {
  const sets = JSON.parse(readFileSync(file, 'utf8')).sets;
  for (const s of sets) if (/\b(from|to|retweets_of|mentions):|(^|[\s(])@\w/i.test(s.query)) throw new Error(`${s.id}: sets may not target accounts (from:, to:, @).`);
  return sets;
}
export const approved = (sets) => sets.filter((s) => s.status === 'approved');

// ------------------------------------------------------------------ search
export async function searchRecent(set, { token, budget, salt, fetchImpl = fetch, maxPages = 1, sinceId } = {}) {
  if (set.status !== 'approved') throw new CapError(`${set.id} is "${set.status}". Only approved keyword sets can run.`);
  const posts = []; let next = null, newest = null;
  for (let page = 0; page < maxPages; page++) {
    const n = budget.allowance(set.maxPerRun || 50);
    if (!n) throw new CapError(`Spending cap reached: ${JSON.stringify(budget.summary())}`);
    const q = new URLSearchParams({ query: set.query, max_results: String(n), 'tweet.fields': FIELDS });
    if (sinceId) q.set('since_id', sinceId);
    if (next) q.set('next_token', next);
    const res = await fetchImpl(`${API}?${q}`, { headers: { Authorization: `Bearer ${token}`, 'User-Agent': 'line-of-blue-ingest/0.1' } });
    if (res.status === 429) throw new ApiError(`Rate limited until ${new Date(+res.headers.get('x-rate-limit-reset') * 1000).toISOString()}.`, 429);
    if (res.status === 402 || res.status === 403) throw new ApiError(`X refused the request (${res.status}). Usually no credit on the account, or the app lacks access. ${await res.text()}`.slice(0, 400), res.status);
    if (!res.ok) throw new ApiError(`X API error ${res.status}: ${(await res.text()).slice(0, 300)}`, res.status);
    const body = await res.json();
    const data = body.data || [];
    budget.record(data.length);
    posts.push(...data.map((tw) => toPost(tw, set, salt)));
    newest = newest || body.meta?.newest_id || null;
    next = body.meta?.next_token;
    if (!next) break;
  }
  return { posts, newestId: newest };
}
