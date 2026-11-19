// node --test web/test.mjs   (no database or network needed; uses the in-memory store)
import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { mkdtempSync, mkdirSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import * as totp from './totp.mjs';
import * as C from './crypto.mjs';
import { MemoryStore } from './store.mjs';
import { createApp, LIMITS } from './server.mjs';

test('TOTP matches the RFC 6238 SHA-1 test vectors', () => {
  const secret = totp.base32Encode(Buffer.from('12345678901234567890'));
  const at = (sec) => totp.codeAt(secret, Math.floor(sec / 30));
  assert.equal(at(59), '287082');
  assert.equal(at(1111111109), '081804');
  assert.equal(at(1234567890), '005924');
  assert.equal(at(2000000000), '279037');
});

test('base32 round-trips and TOTP refuses reuse and old codes', () => {
  const s = totp.newSecret();
  assert.equal(s.length, 32);
  assert.equal(totp.base32Encode(totp.base32Decode(s)), s);
  const now = 1_800_000_000_000, step = totp.stepAt(now);
  const code = totp.codeAt(s, step);
  assert.equal(totp.verify(s, code, { now }), step);
  assert.equal(totp.verify(s, code, { now, lastStep: step }), null, 'replay refused');
  assert.equal(totp.verify(s, totp.codeAt(s, step - 1), { now }), step - 1, 'one step of drift allowed');
  assert.equal(totp.verify(s, totp.codeAt(s, step - 3), { now }), null, 'older codes refused');
  assert.equal(totp.verify(s, 'abcdef', { now }), null);
});

test('passwords hash with scrypt and check correctly', async () => {
  const h = await C.hashPassword('correct horse battery');
  assert.match(h, /^scrypt\$/);
  assert.ok(await C.checkPassword('correct horse battery', h));
  assert.ok(!await C.checkPassword('wrong', h));
  assert.equal(C.recoveryCodes().length, 10);
});

// A small site root with the three pages, so tests do not depend on a build.
function fakeRoot() {
  const r = mkdtempSync(join(tmpdir(), 'lobweb-'));
  mkdirSync(join(r, 'app')); mkdirSync(join(r, 'dist'));
  writeFileSync(join(r, 'app/splash.html'), '<title>Line of Blue</title>\n<h1><a href="https://claude.ai/artifact/BcXAqPCHQ6EEcLMJYCFRSu">x</a></h1>');
  writeFileSync(join(r, 'dist/index.html'), '<!doctype html><title>demo</title>SECRET-DEMO <a href="https://claude.ai/artifact/RwWcXsJHZG1PjgbcuvjyFz">r</a>');
  writeFileSync(join(r, 'dist/research.html'), '<!doctype html><title>research</title>SECRET-RESEARCH');
  return r;
}

async function start(opts = {}) {
  let t = 1_800_000_000_000;
  const clock = { now: () => t, advance: (ms) => { t += ms; } };
  const store = new MemoryStore();
  const server = http.createServer(createApp({ store, setupCode: 'open sesame phrase', root: fakeRoot(), now: clock.now, ...opts }));
  await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
  const base = `http://127.0.0.1:${server.address().port}`;
  const jar = {};
  async function req(path, { form, headers = {}, cookies = true } = {}) {
    const h = { ...headers };
    if (cookies && Object.keys(jar).length) h.cookie = Object.entries(jar).map(([k, v]) => `${k}=${v}`).join('; ');
    if (form) h['content-type'] = 'application/x-www-form-urlencoded';
    const r = await fetch(base + path, { method: form ? 'POST' : 'GET', headers: h, body: form ? new URLSearchParams(form) : undefined, redirect: 'manual' });
    for (const c of r.headers.getSetCookie()) { const [kv, ...rest] = c.split(';'); const [k, v] = kv.split('='); if (/Max-Age=0/.test(rest.join(';'))) delete jar[k]; else jar[k] = v; }
    return { status: r.status, location: r.headers.get('location'), text: await r.text(), headers: r.headers };
  }
  return { server, base, req, jar, store, clock, close: () => new Promise((ok) => server.close(ok)) };
}

async function setUp(s, email = 'owner@example.test', pw = 'a long test password') {
  let r = await s.req('/setup', { form: { setup: 'open sesame phrase', email, password: pw, password2: pw } });
  assert.equal(r.location, '/setup/app');
  r = await s.req('/setup/app');
  const secret = r.text.match(/<div class="secret">([^<]+)<\/div>/)[1].replace(/\s/g, '');
  assert.match(r.text, /data:image\/png;base64,/);
  r = await s.req('/setup/confirm', { form: { code: totp.codeAt(secret, totp.stepAt(s.clock.now())) } });
  assert.equal(r.status, 200);
  const codes = [...r.text.matchAll(/<div>([a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4})<\/div>/g)].map((m) => m[1]);
  assert.equal(codes.length, 10);
  return { secret, codes, email, pw };
}

test('every page is private until the first account is set up and signed in', async () => {
  const s = await start();
  try {
    for (const p of ['/', '/demo', '/research', '/anything']) {
      const r = await s.req(p);
      assert.equal(r.status, 303, p); assert.equal(r.location, '/login');
      assert.ok(!r.text.includes('SECRET'));
    }
    assert.equal((await s.req('/login')).location, '/setup', 'no accounts yet: login sends to setup');
    assert.equal((await s.req('/robots.txt')).text, 'User-agent: *\nDisallow: /\n');
    assert.equal((await s.req('/login')).headers.get('x-robots-tag'), 'noindex, nofollow');
  } finally { await s.close(); }
});

test('setup needs the setup code and closes once an account exists', async () => {
  const s = await start();
  try {
    let r = await s.req('/setup', { form: { setup: 'wrong', email: 'a@b.test', password: 'x'.repeat(12), password2: 'x'.repeat(12) } });
    assert.equal(r.status, 401);
    r = await s.req('/setup', { form: { setup: 'open sesame phrase', email: 'a@b.test', password: 'short', password2: 'short' } });
    assert.equal(r.status, 400);
    const { codes } = await setUp(s);
    // Setup signs you straight in.
    r = await s.req('/');
    assert.equal(r.status, 200); assert.match(r.text, /href="\/demo"/, 'splash links to the hosted demo');
    r = await s.req('/demo');
    assert.match(r.text, /SECRET-DEMO/); assert.match(r.text, /href="\/research"/);
    assert.match(r.headers.get('content-security-policy'), /frame-ancestors 'none'/);
    // A second setup attempt is refused.
    delete s.jar.lob_session;
    r = await s.req('/setup', { form: { setup: 'open sesame phrase', email: 'x@y.test', password: 'y'.repeat(12), password2: 'y'.repeat(12) } });
    assert.equal(r.location, '/login');
    assert.equal(await s.store.countUsers(), 1);
    assert.equal(codes.length, 10);
  } finally { await s.close(); }
});

test('setup is switched off without LOB_SETUP_CODE', async () => {
  const s = await start({ setupCode: '' });
  try {
    const r = await s.req('/setup');
    assert.match(r.text, /LOB_SETUP_CODE/);
    const p = await s.req('/setup', { form: { setup: '', email: 'a@b.test', password: 'x'.repeat(12), password2: 'x'.repeat(12) } });
    assert.equal(p.location, '/login');
    assert.equal(await s.store.countUsers(), 0);
  } finally { await s.close(); }
});

test('sign-in needs password then authenticator code; codes cannot be reused', async () => {
  const s = await start();
  try {
    const { secret, email, pw } = await setUp(s);
    await s.req('/logout', { form: {} });
    assert.equal((await s.req('/demo')).location, '/login', 'signed out');

    // Password alone is not enough.
    let r = await s.req('/login', { form: { email, password: pw } });
    assert.equal(r.location, '/login/code');
    assert.equal((await s.req('/demo')).location, '/login');

    r = await s.req('/login/code', { form: { code: '000000' } });
    assert.equal(r.status, 401);
    s.clock.advance(31000);
    const code = totp.codeAt(secret, totp.stepAt(s.clock.now()));
    r = await s.req('/login/code', { form: { code } });
    assert.equal(r.location, '/');
    assert.equal((await s.req('/demo')).status, 200);

    // The same code again (new password step) is refused.
    await s.req('/logout', { form: {} });
    await s.req('/login', { form: { email, password: pw } });
    r = await s.req('/login/code', { form: { code } });
    assert.equal(r.status, 401);
  } finally { await s.close(); }
});

test('wrong password and unknown email give the same answer', async () => {
  const s = await start();
  try {
    const { email } = await setUp(s);
    delete s.jar.lob_session;
    const a = await s.req('/login', { form: { email, password: 'wrong password here' } });
    const b = await s.req('/login', { form: { email: 'nobody@example.test', password: 'wrong password here' } });
    assert.equal(a.status, 401); assert.equal(b.status, 401);
    assert.match(a.text, /do not match/); assert.match(b.text, /do not match/);
  } finally { await s.close(); }
});

test('recovery codes work once each', async () => {
  const s = await start();
  try {
    const { codes, email, pw } = await setUp(s);
    await s.req('/logout', { form: {} });
    await s.req('/login', { form: { email, password: pw } });
    let r = await s.req('/login/code', { form: { code: codes[0].toUpperCase() } });
    assert.equal(r.location, '/');
    await s.req('/logout', { form: {} });
    await s.req('/login', { form: { email, password: pw } });
    r = await s.req('/login/code', { form: { code: codes[0] } });
    assert.equal(r.status, 401);
  } finally { await s.close(); }
});

test('five wrong attempts lock the account for 15 minutes', async () => {
  const s = await start();
  try {
    const { secret, email, pw } = await setUp(s);
    delete s.jar.lob_session;
    for (let i = 0; i < LIMITS.maxFails; i++) await s.req('/login', { form: { email, password: 'wrong password ' + i } });
    let r = await s.req('/login', { form: { email, password: pw } });
    assert.equal(r.status, 429, 'locked even with the right password');
    s.clock.advance(LIMITS.lockMs + 1000);
    r = await s.req('/login', { form: { email, password: pw } });
    assert.equal(r.location, '/login/code');
    r = await s.req('/login/code', { form: { code: totp.codeAt(secret, totp.stepAt(s.clock.now())) } });
    assert.equal(r.location, '/');
  } finally { await s.close(); }
});

test('sessions expire, and forms from other sites are refused', async () => {
  const s = await start();
  try {
    const { email, pw } = await setUp(s);
    assert.equal((await s.req('/demo')).status, 200);
    s.clock.advance(LIMITS.sessionMs + 1000);
    assert.equal((await s.req('/demo')).location, '/login');
    const r = await s.req('/login', { form: { email, password: pw }, headers: { origin: 'https://evil.example' } });
    assert.equal(r.status, 403);
    assert.equal((await s.req('/login', { form: { email, password: pw }, headers: { 'sec-fetch-site': 'cross-site' } })).status, 403);
    assert.equal((await s.req('/login', { form: { email, password: pw }, headers: { 'sec-fetch-site': 'same-site' } })).status, 403);
    // A pending (password-only) cookie never opens pages.
    await s.req('/login', { form: { email, password: pw } });
    s.jar.lob_session = s.jar.lob_pending;
    assert.equal((await s.req('/demo')).location, '/login');
  } finally { await s.close(); }
});

test('behind https, cookies are Secure, HttpOnly and __Host- prefixed', async () => {
  const s = await start();
  try {
    const r = await s.req('/setup', { form: { setup: 'open sesame phrase', email: 'a@b.test', password: 'x'.repeat(12), password2: 'x'.repeat(12) }, headers: { 'x-forwarded-proto': 'https' } });
    const c = r.headers.getSetCookie()[0];
    assert.match(c, /^__Host-lob_setup=/); assert.match(c, /Secure/); assert.match(c, /HttpOnly/); assert.match(c, /SameSite=Lax/);
    assert.match(r.headers.get('strict-transport-security'), /max-age=/);
  } finally { await s.close(); }
});
