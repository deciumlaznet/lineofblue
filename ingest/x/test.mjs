// node --test ingest/x/test.mjs   (no network, no credit needed)
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Budget, pseudonym, scrub, toPost, loadSets, searchRecent, CapError } from './connector.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const fixture = JSON.parse(readFileSync(join(here, 'fixture.json'), 'utf8'));
const SALT = 'test-salt-0123456789';
const tmp = () => join(mkdtempSync(join(tmpdir(), 'lob-')), 'ledger.json');
const budget = (o = {}) => new Budget({ file: tmp(), dailyCap: 100, monthlyCap: 1000, pricePerPost: 0.005, now: () => new Date('2026-11-19T10:00:00Z'), ...o });
const set = { id: 'XS-T', query: 'police lang:en', status: 'approved', maxPerRun: 50 };
const okFetch = (calls) => async (url) => { calls.push(url); return { ok: true, status: 200, json: async () => fixture, headers: new Map() }; };

test('pseudonyms are stable, salted and never the raw id', () => {
  assert.equal(pseudonym('111', SALT), pseudonym('111', SALT));
  assert.notEqual(pseudonym('111', SALT), pseudonym('111', SALT + 'x'));
  assert.ok(!pseudonym('111', SALT).includes('111'));
  assert.throws(() => pseudonym('111', ''), /X_PSEUDONYM_SALT/);
});

test('handles and profile links are scrubbed from text', () => {
  assert.equal(scrub('hi @someone see https://x.com/someone/status/1'), 'hi @user see [link]');
});

test('posts map to the demo post shape with no author details', () => {
  const p = toPost(fixture.data[0], set, SALT);
  assert.deepEqual(Object.keys(p).sort(), ['account', 'flags', 'id', 'lang', 'narrative', 'place', 'platform', 'reach', 'set', 'shares', 'source', 'synthetic', 't', 'text']);
  assert.equal(p.platform, 'x'); assert.equal(p.synthetic, false); assert.equal(p.reach, 820); assert.equal(p.shares, 5);
  assert.ok(!JSON.stringify(p).includes('111') && !JSON.stringify(p).includes('someone'));
});

test('sets that target accounts are refused', () => {
  const f = join(dirname(tmp()), 'q.json');
  for (const q of ['from:someone police', 'police @someone', 'to:someone']) {
    writeFileSync(f, JSON.stringify({ sets: [{ id: 'B', query: q, status: 'approved' }] }));
    assert.throws(() => loadSets(f), /may not target accounts/);
  }
  assert.equal(loadSets(join(here, 'queries.json')).length >= 1, true);
});

test('only approved sets run', async () => {
  await assert.rejects(searchRecent({ ...set, status: 'proposed' }, { token: 't', budget: budget(), salt: SALT, fetchImpl: okFetch([]) }), CapError);
});

test('request size is cut to what the cap allows, and reads are recorded', async () => {
  const b = budget({ dailyCap: 30 }), calls = [];
  const { posts } = await searchRecent(set, { token: 't', budget: b, salt: SALT, fetchImpl: okFetch(calls) });
  assert.equal(posts.length, 2);
  assert.match(calls[0], /max_results=30/);
  assert.equal(b.used().day, 2);
});

test('no request is sent once the cap is reached', async () => {
  const b = budget({ dailyCap: 100, monthlyCap: 105 }); b.record(100);
  const calls = [];
  await assert.rejects(searchRecent(set, { token: 't', budget: b, salt: SALT, fetchImpl: okFetch(calls) }), /Spending cap reached/);
  assert.equal(calls.length, 0);
});

test('the ledger persists across runs and resets each day', () => {
  const file = tmp();
  const a = new Budget({ file, dailyCap: 100, monthlyCap: 1000, pricePerPost: 0.005, now: () => new Date('2026-11-19T10:00:00Z') }); a.record(40);
  const b = new Budget({ file, dailyCap: 100, monthlyCap: 1000, pricePerPost: 0.005, now: () => new Date('2026-11-19T23:00:00Z') });
  assert.equal(b.used().day, 40);
  const c = new Budget({ file, dailyCap: 100, monthlyCap: 1000, pricePerPost: 0.005, now: () => new Date('2026-11-20T01:00:00Z') });
  assert.deepEqual(c.used(), { day: 0, month: 40 });
  assert.equal(c.summary().estimatedSpendThisMonthUSD, 0.2);
});

test('no credit (402) gives a clear message', async () => {
  const f = async () => ({ ok: false, status: 402, text: async () => 'CreditsDepleted', headers: new Map() });
  await assert.rejects(searchRecent(set, { token: 't', budget: budget(), salt: SALT, fetchImpl: f }), /no credit/);
});
