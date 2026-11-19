#!/usr/bin/env node
// Search-term tuning. Runs each query variant in a probe file once (10 posts each, the minimum X allows),
// inside the normal daily and monthly caps, and saves what came back so the hits can be scored for relevance.
// Nothing goes into the live data. Usage: node ingest/x/probe.mjs ingest/x/probes/round1.json [--dry-run]
import { fileURLToPath } from 'node:url';
import { dirname, join, basename, resolve } from 'node:path';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { Budget, searchRecent, CapError, loadSets } from './connector.mjs';

const here = dirname(fileURLToPath(import.meta.url)), root = join(here, '..', '..');
const args = process.argv.slice(2), dry = args.includes('--dry-run'), file = args.find((a) => !a.startsWith('--'));
if (!file) { console.error('Usage: node ingest/x/probe.mjs <probe file> [--dry-run]'); process.exit(2); }
const env = process.env, outDir = env.LOB_INGEST_DIR || join(root, 'data', 'ingest');
const budget = new Budget({ file: join(outDir, dry ? 'x-ledger-dryrun.json' : 'x-ledger.json'), dailyCap: +(env.X_DAILY_POST_CAP || 100), monthlyCap: +(env.X_MONTHLY_POST_CAP || 3000), pricePerPost: +(env.X_PRICE_PER_POST_USD || 0.005) });
const variants = loadSets(resolve(file)).map((v) => ({ ...v, status: 'approved', maxPerRun: 10 }));
const token = dry ? 'dry-run' : env.X_BEARER_TOKEN, salt = dry ? 'dry-run-salt-0000' : env.X_PSEUDONYM_SALT;
const fixture = JSON.parse(readFileSync(join(here, 'fixture.json'), 'utf8'));
const fetchImpl = dry ? async () => ({ ok: true, status: 200, json: async () => fixture, headers: new Map() }) : fetch;

const report = { probe: basename(file), ran: new Date().toISOString(), variants: [] };
for (const v of variants) {
  try {
    const { posts } = await searchRecent(v, { token, budget, salt, fetchImpl });
    report.variants.push({ id: v.id, topic: v.label, query: v.query, returned: posts.length, samples: posts.map((p) => ({ text: p.text, lang: p.lang, reach: p.reach })) });
    console.log(`${v.id}: ${posts.length} posts`);
  } catch (e) {
    report.variants.push({ id: v.id, topic: v.label, query: v.query, error: e.message });
    console.error(`${v.id}: ${e.message}`); if (e instanceof CapError) break;
  }
}
mkdirSync(outDir, { recursive: true });
const out = join(outDir, `x-probe-${basename(file, '.json')}${dry ? '-dryrun' : ''}.json`);
writeFileSync(out, JSON.stringify(report, null, 1));
console.log(`Saved ${out}`); console.log(JSON.stringify(budget.summary()));
