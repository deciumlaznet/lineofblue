#!/usr/bin/env node
// Usage: node ingest/x/run.mjs [--set XS-01] [--dry-run] [--status]
// Live runs need the Replit secrets X_BEARER_TOKEN and X_PSEUDONYM_SALT.
// Caps (env, optional): X_DAILY_POST_CAP (default 100), X_MONTHLY_POST_CAP (default 3000),
// X_PRICE_PER_POST_USD (default 0.005, used only for the spend estimate).
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { appendFileSync, mkdirSync, readFileSync } from 'node:fs';
import { Budget, loadSets, approved, searchRecent, CapError } from './connector.mjs';

const here = dirname(fileURLToPath(import.meta.url)), root = join(here, '..', '..');
const args = process.argv.slice(2), flag = (f) => args.includes(f), val = (f) => (args.includes(f) ? args[args.indexOf(f) + 1] : null);
const env = process.env, dry = flag('--dry-run');
const outDir = env.LOB_INGEST_DIR || join(root, 'data', 'ingest');
const budget = new Budget({ file: join(outDir, dry ? 'x-ledger-dryrun.json' : 'x-ledger.json'), dailyCap: +(env.X_DAILY_POST_CAP || 100), monthlyCap: +(env.X_MONTHLY_POST_CAP || 3000), pricePerPost: +(env.X_PRICE_PER_POST_USD || 0.005) });
if (flag('--status')) { console.log(JSON.stringify(budget.summary(), null, 1)); process.exit(0); }

let sets = loadSets(join(here, 'queries.json'));
if (dry) sets = sets.map((s) => ({ ...s, status: 'approved' }));
const want = val('--set'); sets = approved(sets).filter((s) => !want || s.id === want);
if (!sets.length) { console.error('No approved keyword set to run. Approve one in ingest/x/queries.json (status "approved").'); process.exit(2); }
const token = dry ? 'dry-run' : env.X_BEARER_TOKEN, salt = dry ? 'dry-run-salt-0000' : env.X_PSEUDONYM_SALT;
if (!token) { console.error('X_BEARER_TOKEN is not set.'); process.exit(2); }
const fixture = JSON.parse(readFileSync(join(here, 'fixture.json'), 'utf8'));
const fetchImpl = dry ? async () => ({ ok: true, status: 200, json: async () => fixture, headers: new Map() }) : fetch;

mkdirSync(outDir, { recursive: true });
const out = join(outDir, `x-${new Date().toISOString().slice(0, 10)}${dry ? '-dryrun' : ''}.jsonl`);
for (const set of sets) {
  try {
    const { posts } = await searchRecent(set, { token, budget, salt, fetchImpl });
    posts.forEach((p) => appendFileSync(out, JSON.stringify(p) + '\n'));
    console.log(`${set.id}: ${posts.length} posts -> ${out}`);
  } catch (e) { console.error(`${set.id}: ${e.message}`); if (e instanceof CapError) break; }
}
console.log(JSON.stringify(budget.summary()));
