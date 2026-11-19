// Password hashing (scrypt), random tokens and recovery codes.
import { scrypt, randomBytes, timingSafeEqual, createHash } from 'node:crypto';

const N = 32768, r = 8, p = 1, KEYLEN = 64, MAXMEM = 128 * 1024 * 1024;
const run = (pw, salt, n = N) => new Promise((ok, no) =>
  scrypt(String(pw).normalize('NFKC'), salt, KEYLEN, { N: n, r, p, maxmem: MAXMEM }, (e, k) => e ? no(e) : ok(k)));

export async function hashPassword(pw) {
  const salt = randomBytes(16);
  const key = await run(pw, salt);
  return `scrypt$${N}$${salt.toString('base64')}$${key.toString('base64')}`;
}

export async function checkPassword(pw, stored) {
  const [kind, n, salt, key] = String(stored || '').split('$');
  if (kind !== 'scrypt' || !salt || !key) return false;
  const got = await run(pw, Buffer.from(salt, 'base64'), Number(n));
  const want = Buffer.from(key, 'base64');
  return got.length === want.length && timingSafeEqual(got, want);
}

// A fixed hash so a wrong email takes as long as a wrong password.
let dummy;
export async function burnTime(pw) { dummy ||= await hashPassword('not-a-real-password'); await checkPassword(pw, dummy); }

export const token = () => randomBytes(32).toString('base64url');
export const sha256 = (s) => createHash('sha256').update(String(s)).digest('hex');

// Ten codes like "k7q2-9xdm-4tfp", shown once; only their hashes are kept.
const RC = 'abcdefghjkmnpqrstuvwxyz23456789';
export function recoveryCodes(n = 10) {
  return Array.from({ length: n }, () => {
    const b = randomBytes(12); let s = '';
    for (let i = 0; i < 12; i++) s += RC[b[i] % RC.length];
    return `${s.slice(0, 4)}-${s.slice(4, 8)}-${s.slice(8)}`;
  });
}
export const normRecovery = (c) => String(c || '').toLowerCase().replace(/[^a-z0-9]/g, '');

export function safeEqual(a, b) {
  const x = Buffer.from(sha256(a)), y = Buffer.from(sha256(b));
  return timingSafeEqual(x, y) && String(a) === String(b);
}
