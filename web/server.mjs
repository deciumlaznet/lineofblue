// Line of Blue private site. Every page needs a signed-in session: a password, then a 6-digit code from an
// authenticator app (or a one-time recovery code), or "Sign in with Google" (web/google.mjs) for an account's own
// email or an ADMIN_EMAILS address. Only /login, /login/google, /setup, /robots.txt and /healthz are open.
//   DATABASE_URL     Postgres for accounts and sessions (Replit provides it). Without it, accounts live in memory.
//   LOB_SETUP_CODE   phrase needed to create the first account at /setup. /setup closes once an account exists.
//   PORT             default 5000
import http from 'node:http';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import QRCode from 'qrcode';
import * as totp from './totp.mjs';
import * as C from './crypto.mjs';
import * as P from './pages.mjs';
import { adminEmailsFromEnv, decodeFlow, encodeFlow, GoogleSignIn } from './google.mjs';
import { MemoryStore, PgStore } from './store.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const MIN = 60 * 1000;
export const LIMITS = { sessionMs: 12 * 60 * MIN, pendingMs: 5 * MIN, setupMs: 15 * MIN, maxFails: 5, lockMs: 15 * MIN, ipMax: 30, ipWindowMs: 15 * MIN };

const DEMO_ARTIFACT = 'https://claude.ai/artifact/BcXAqPCHQ6EEcLMJYCFRSu';
const RESEARCH_ARTIFACT = 'https://claude.ai/artifact/RwWcXsJHZG1PjgbcuvjyFz';
const localLinks = (html) => html.split(DEMO_ARTIFACT).join('/demo').split(RESEARCH_ARTIFACT).join('/research');

function loadPages(root) {
  const read = (p) => existsSync(join(root, p)) ? readFileSync(join(root, p), 'utf8') : null;
  const splash = read('app/splash.html');
  return {
    '/': splash && localLinks(`<!doctype html>\n<html lang="en-GB">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="robots" content="noindex, nofollow">\n${splash.replace('<h1', '</head>\n<body>\n<h1')}\n</body>\n</html>\n`),
    '/demo': read('dist/index.html') && localLinks(read('dist/index.html')),
    '/research': read('dist/research.html') && localLinks(read('dist/research.html')),
  };
}

const BASE_HEADERS = {
  'X-Robots-Tag': 'noindex, nofollow',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Referrer-Policy': 'same-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  'Cross-Origin-Opener-Policy': 'same-origin',
  'Cache-Control': 'no-store',
};
const AUTH_CSP = "default-src 'none'; style-src 'unsafe-inline'; img-src data:; form-action 'self'; base-uri 'none'; frame-ancestors 'none'";
const SITE_CSP = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'";

function parseCookies(h = '') {
  const out = {};
  for (const part of h.split(';')) { const i = part.indexOf('='); if (i > 0) out[part.slice(0, i).trim()] = decodeURIComponent(part.slice(i + 1).trim()); }
  return out;
}

async function readForm(req, limit = 8192) {
  let size = 0; const chunks = [];
  for await (const c of req) { size += c.length; if (size > limit) throw Object.assign(new Error('too big'), { status: 413 }); chunks.push(c); }
  return Object.fromEntries(new URLSearchParams(Buffer.concat(chunks).toString('utf8')));
}

export function createApp({ store, setupCode = '', root = ROOT, now = () => Date.now(), secureCookies, google, adminEmails = adminEmailsFromEnv(undefined) } = {}) {
  const pages = loadPages(root);
  const hits = new Map();

  const isSecure = (req) => secureCookies ?? (req.headers['x-forwarded-proto'] === 'https');
  const name = (req, n) => isSecure(req) ? `__Host-${n}` : n;
  const cookie = (req, n, v, ms) => `${name(req, n)}=${v}; Path=/; HttpOnly; SameSite=Lax${isSecure(req) ? '; Secure' : ''}; Max-Age=${Math.floor(ms / 1000)}`;
  const clear = (req, n) => cookie(req, n, '', 0);
  const ip = (req) => String(req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').split(',')[0].trim();

  function send(res, status, body, { csp = AUTH_CSP, type = 'text/html; charset=utf-8', headers = {}, req } = {}) {
    const h = { ...BASE_HEADERS, 'Content-Type': type, 'Content-Security-Policy': csp, ...headers };
    if (req && isSecure(req)) h['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains';
    res.writeHead(status, h); res.end(body);
  }
  const redirect = (res, to, req, cookies = []) => send(res, 303, '', { req, headers: { Location: to, ...(cookies.length ? { 'Set-Cookie': cookies } : {}) } });

  // Too many sign-in posts from one address in the window: refuse for a while.
  function ipLimited(req) {
    const t = now(), k = ip(req);
    const list = (hits.get(k) || []).filter((x) => t - x < LIMITS.ipWindowMs);
    list.push(t); hits.set(k, list);
    if (hits.size > 10000) hits.clear();
    return list.length > LIMITS.ipMax;
  }

  // Refuse form posts sent from another site.
  // Browsers say where a form came from in Sec-Fetch-Site; older ones only send Origin.
  function crossSite(req) {
    const site = req.headers['sec-fetch-site'];
    if (site) return !(site === 'same-origin' || site === 'none');
    const origin = req.headers.origin;
    if (!origin) return false;
    const hosts = [req.headers.host, ...String(req.headers['x-forwarded-host'] || '').split(',')].map((h) => String(h || '').trim()).filter(Boolean);
    try { return !hosts.includes(new URL(origin).host); } catch { return true; }
  }

  async function sessionOf(req, kind) {
    const v = parseCookies(req.headers.cookie)[name(req, kind)];
    if (!v) return null;
    const s = await store.getSession(C.sha256(v));
    return s && s.expiresAt > now() ? { ...s, raw: v } : null;
  }

  async function newSession(userId, stage, ms) {
    const t = C.token();
    await store.putSession({ tokenHash: C.sha256(t), userId, stage, expiresAt: now() + ms });
    return t;
  }

  async function fail(user) {
    const failedCount = (user.failedCount || 0) + 1;
    const lock = failedCount >= LIMITS.maxFails;
    await store.updateUser(user.id, { failedCount: lock ? 0 : failedCount, lockedUntil: lock ? now() + LIMITS.lockMs : user.lockedUntil || 0 });
  }
  const locked = (u) => u && u.lockedUntil > now();
  const LOCKED_MSG = 'Too many attempts. Wait 15 minutes and try again.';
  const loginPage = (e, email) => P.loginPage(e, email, { google: Boolean(google) });
  async function adminOf(req) {
    const s = await sessionOf(req, 'lob_session');
    if (!s || s.stage !== 'full') return null;
    const u = await store.getUser(s.userId);
    return u && (adminEmails.includes(u.email) || u.id === 1 || u.id === '1') ? u : null;
  }

  // The account a verified Google email may use: the account with that email, or for an admin email with no
  // account yet, a new account that can only be reached through Google (random password, no recovery codes).
  async function accountForGoogle(email) {
    const user = await store.getUserByEmail(email);
    if (user) return user;
    if (!adminEmails.includes(email)) return null;
    try { return await store.createUser({ email, pwHash: await C.hashPassword(C.token()), totpSecret: totp.newSecret(), recovery: [], lastStep: -1 }); }
    catch { return store.getUserByEmail(email); }
  }

  const routes = {
    'GET /robots.txt': (req, res) => send(res, 200, 'User-agent: *\nDisallow: /\n', { type: 'text/plain; charset=utf-8', req }),
    'GET /healthz': (req, res) => send(res, 200, 'ok', { type: 'text/plain; charset=utf-8', req }),

    'GET /login': async (req, res) => {
      if (!google && await store.countUsers() === 0) return redirect(res, '/setup', req);
      if (await sessionOf(req, 'lob_session')) return redirect(res, '/', req);
      send(res, 200, loginPage(new URL(req.url, 'http://x').searchParams.get('err') || ''), { req });
    },
    'POST /login': async (req, res, f) => {
      if (ipLimited(req)) return send(res, 429, loginPage(LOCKED_MSG), { req });
      const email = String(f.email || '').trim().toLowerCase(), pw = String(f.password || '');
      const user = await store.getUserByEmail(email);
      if (locked(user)) return send(res, 429, loginPage(LOCKED_MSG, email), { req });
      const ok = user ? await C.checkPassword(pw, user.pwHash) : (await C.burnTime(pw), false);
      if (!ok) { if (user) await fail(user); return send(res, 401, loginPage('That email and password do not match.', email), { req }); }
      const t = await newSession(user.id, 'pending', LIMITS.pendingMs);
      redirect(res, '/login/code', req, [cookie(req, 'lob_pending', t, LIMITS.pendingMs)]);
    },
    'GET /login/code': async (req, res) => {
      if (!await sessionOf(req, 'lob_pending')) return redirect(res, '/login', req);
      send(res, 200, P.codePage(), { req });
    },
    'POST /login/code': async (req, res, f) => {
      const pending = await sessionOf(req, 'lob_pending');
      if (!pending || pending.stage !== 'pending') return redirect(res, '/login', req);
      if (ipLimited(req)) return send(res, 429, P.codePage(LOCKED_MSG), { req });
      const user = await store.getUser(pending.userId);
      if (!user || locked(user)) { await store.deleteSession(pending.tokenHash); return send(res, 429, loginPage(LOCKED_MSG), { req, headers: { 'Set-Cookie': clear(req, 'lob_pending') } }); }
      const code = String(f.code || '').trim();
      let ok = false;
      if (/^\d[\d\s]{5,6}$/.test(code)) {
        const step = totp.verify(user.totpSecret, code, { now: now(), lastStep: user.lastStep });
        ok = step !== null && await store.claimStep(user.id, step);
      } else if (C.normRecovery(code).length === 12) {
        ok = await store.useRecovery(user.id, C.sha256(C.normRecovery(code)));
      }
      if (!ok) { await fail(user); return send(res, 401, P.codePage('That code is not right. Codes change every 30 seconds.'), { req }); }
      await store.deleteSession(pending.tokenHash);
      await store.updateUser(user.id, { failedCount: 0, lockedUntil: 0 });
      const t = await newSession(user.id, 'full', LIMITS.sessionMs);
      redirect(res, '/', req, [clear(req, 'lob_pending'), cookie(req, 'lob_session', t, LIMITS.sessionMs)]);
    },

    'GET /login/google': async (req, res) => {
      if (!google) return redirect(res, '/login', req);
      const { flow, url } = google.start();
      send(res, 302, '', { req, headers: { Location: url, 'Set-Cookie': cookie(req, 'lob_google', encodeFlow(flow), 10 * MIN) } });
    },
    'GET /login/google/callback': async (req, res) => {
      const back = (msg) => redirect(res, `/login?err=${encodeURIComponent(msg)}`, req, [clear(req, 'lob_google')]);
      if (!google) return redirect(res, '/login', req);
      if (ipLimited(req)) return back(LOCKED_MSG);
      let id;
      try { id = await google.finish(decodeFlow(parseCookies(req.headers.cookie)[name(req, 'lob_google')]), Object.fromEntries(new URL(req.url, 'http://x').searchParams)); }
      catch (e) { return back(e.message || 'Google sign-in failed. Please try again.'); }
      const user = await accountForGoogle(id.email);
      if (!user) { console.log('signin.google.unknown'); return back(`${id.email} does not have a Line of Blue account.`); }
      if (locked(user)) return back(LOCKED_MSG);
      await store.updateUser(user.id, { failedCount: 0, lockedUntil: 0 });
      const t = await newSession(user.id, 'full', LIMITS.sessionMs);
      console.log('signin.google', id.email.replace(/^(.).*@/, '$1…@'));
      redirect(res, '/', req, [clear(req, 'lob_google'), cookie(req, 'lob_session', t, LIMITS.sessionMs)]);
    },

    // Admins (ADMIN_EMAILS, or the first account) can add members, such as tester accounts.
    'GET /members': async (req, res) => {
      if (!await adminOf(req)) return redirect(res, '/login', req);
      send(res, 200, P.membersPage(), { req });
    },
    'POST /members': async (req, res, f) => {
      if (!await adminOf(req)) return redirect(res, '/login', req);
      const email = String(f.email || '').trim().toLowerCase(), pw = String(f.password || '');
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return send(res, 400, P.membersPage('Enter a valid email address.', email), { req });
      if (pw.length < 12) return send(res, 400, P.membersPage('Use a password of at least 12 characters.', email), { req });
      if (pw !== String(f.password2 || '')) return send(res, 400, P.membersPage('The two passwords do not match.', email), { req });
      if (await store.getUserByEmail(email)) return send(res, 409, P.membersPage('That email already has an account.', email), { req });
      const secret = totp.newSecret(), codes = C.recoveryCodes();
      try { await store.createUser({ email, pwHash: await C.hashPassword(pw), totpSecret: secret, recovery: codes.map((c) => C.sha256(C.normRecovery(c))), lastStep: -1 }); }
      catch { return send(res, 409, P.membersPage('That email already has an account.', email), { req }); }
      const qr = await QRCode.toDataURL(totp.otpauthUrl(secret, email), { margin: 0, width: 220, errorCorrectionLevel: 'M' });
      send(res, 200, P.memberCreatedPage(email, qr, secret, codes), { req });
    },

    'GET /logout': (req, res) => send(res, 200, P.logoutPage(), { req }),
    'POST /logout': async (req, res) => {
      const s = await sessionOf(req, 'lob_session');
      if (s) await store.deleteSession(s.tokenHash);
      redirect(res, '/login', req, [clear(req, 'lob_session')]);
    },

    'GET /setup': async (req, res) => {
      if (await store.countUsers() > 0) return redirect(res, '/login', req);
      send(res, 200, setupCode ? P.setupPage() : P.setupMissingPage(), { req });
    },
    'POST /setup': async (req, res, f) => {
      if (await store.countUsers() > 0 || !setupCode) return redirect(res, '/login', req);
      if (ipLimited(req)) return send(res, 429, P.setupPage(LOCKED_MSG), { req });
      const email = String(f.email || '').trim().toLowerCase(), pw = String(f.password || '');
      if (!C.safeEqual(String(f.setup || ''), setupCode)) return send(res, 401, P.setupPage('That setup code is not right.', email), { req });
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return send(res, 400, P.setupPage('Enter a valid email address.', email), { req });
      if (pw.length < 12) return send(res, 400, P.setupPage('Use a password of at least 12 characters.', email), { req });
      if (pw !== String(f.password2 || '')) return send(res, 400, P.setupPage('The two passwords do not match.', email), { req });
      const t = C.token();
      await store.putSetup({ tokenHash: C.sha256(t), email, pwHash: await C.hashPassword(pw), totpSecret: totp.newSecret(), expiresAt: now() + LIMITS.setupMs });
      redirect(res, '/setup/app', req, [cookie(req, 'lob_setup', t, LIMITS.setupMs)]);
    },
    'GET /setup/app': async (req, res, f, e) => {
      const v = parseCookies(req.headers.cookie)[name(req, 'lob_setup')];
      const s = v && await store.getSetup(C.sha256(v));
      if (!s || await store.countUsers() > 0) return redirect(res, '/setup', req);
      const qr = await QRCode.toDataURL(totp.otpauthUrl(s.totpSecret, s.email), { margin: 0, width: 220, errorCorrectionLevel: 'M' });
      send(res, e ? 401 : 200, P.setupAppPage(qr, s.totpSecret, e), { req });
    },
    'POST /setup/confirm': async (req, res, f) => {
      const v = parseCookies(req.headers.cookie)[name(req, 'lob_setup')];
      const s = v && await store.getSetup(C.sha256(v));
      if (!s || await store.countUsers() > 0) return redirect(res, '/setup', req);
      if (ipLimited(req)) return send(res, 429, P.messagePage('Too many attempts', LOCKED_MSG), { req });
      const step = totp.verify(s.totpSecret, f.code, { now: now() });
      if (step === null) return routes['GET /setup/app'](req, res, f, 'That code is not right. Check the time on your phone is set automatically.');
      const codes = C.recoveryCodes();
      let user;
      try { user = await store.createUser({ email: s.email, pwHash: s.pwHash, totpSecret: s.totpSecret, recovery: codes.map((c) => C.sha256(C.normRecovery(c))), lastStep: step }); }
      catch { return redirect(res, '/login', req); }
      await store.deleteSetup(s.tokenHash);
      const t = await newSession(user.id, 'full', LIMITS.sessionMs);
      send(res, 200, P.recoveryPage(codes), { req, headers: { 'Set-Cookie': [clear(req, 'lob_setup'), cookie(req, 'lob_session', t, LIMITS.sessionMs)] } });
    },
  };

  return async function handle(req, res) {
    try {
      const url = new URL(req.url, 'http://x');
      const path = url.pathname.length > 1 ? url.pathname.replace(/\/+$/, '') : '/';
      const method = req.method === 'HEAD' ? 'GET' : req.method;
      const route = routes[`${method} ${path}`];
      if (route) {
        let form = {};
        if (method === 'POST') {
          if (crossSite(req)) return send(res, 403, P.messagePage('Refused', 'This form must be sent from this site.'), { req });
          form = await readForm(req);
        }
        return await route(req, res, form);
      }
      if (method !== 'GET') return send(res, 405, 'Method not allowed', { type: 'text/plain; charset=utf-8', req });
      const s = await sessionOf(req, 'lob_session');
      if (!s || s.stage !== 'full') return redirect(res, '/login', req);
      const body = pages[path];
      if (body === undefined) return send(res, 404, P.messagePage('Not found', 'There is no page here.'), { req });
      if (body === null) return send(res, 503, P.messagePage('Not built yet', 'Run python3 scripts/build.py, then publish again.'), { req });
      send(res, 200, body, { csp: SITE_CSP, req });
    } catch (e) {
      if (!res.headersSent) send(res, e.status || 500, P.messagePage('Something went wrong', 'Please try again.'), { req });
      if (!e.status) console.error(e);
    }
  };
}

export async function main() {
  const store = process.env.DATABASE_URL ? new PgStore(process.env.DATABASE_URL) : new MemoryStore();
  if (!process.env.DATABASE_URL) console.warn('DATABASE_URL is not set: accounts are kept in memory and lost on restart.');
  await store.init();
  const google = GoogleSignIn.fromEnv(process.env);
  if (!google) console.warn('GOOGLE_SIGNIN_CLIENT_ID / GOOGLE_SIGNIN_CLIENT_SECRET not set: Google sign-in is off.');
  const handle = createApp({ store, setupCode: process.env.LOB_SETUP_CODE || '', secureCookies: process.env.NODE_ENV === 'production' ? true : undefined,
    google, adminEmails: adminEmailsFromEnv(process.env.ADMIN_EMAILS) });
  const port = Number(process.env.PORT || 5000);
  http.createServer(handle).listen(port, '0.0.0.0', () => console.log(`Line of Blue site on port ${port}`));
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) main();
