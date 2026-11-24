// "Sign in with Google" for the Line of Blue site. No packages.
// OpenID Connect authorisation code flow with PKCE, state and nonce. The ID token comes straight back from
// Google's token endpoint over TLS, so its claims are trusted after checking issuer, audience, expiry, nonce
// and that Google has verified the email. Google only proves who someone is: server.mjs decides who may in.
//   GOOGLE_SIGNIN_CLIENT_ID / GOOGLE_SIGNIN_CLIENT_SECRET   the OAuth client; Google sign-in is off without them
//   SITE_URL or GOOGLE_SIGNIN_REDIRECT_URI                   default https://www.lineofblue.co.uk/login/google/callback
//   ADMIN_EMAILS                                            default expeditionup@gmail.com; "none" turns it off
import { createHash, randomBytes } from 'node:crypto';

const GOOGLE_AUTHORIZE = 'https://accounts.google.com/o/oauth2/v2/auth';
const GOOGLE_TOKEN = 'https://oauth2.googleapis.com/token';
const ISSUERS = new Set(['https://accounts.google.com', 'accounts.google.com']);

/** ADMIN_EMAILS (comma-separated). Defaults to the owner's Google account; "none" turns it off. */
export function adminEmailsFromEnv(value) {
  const raw = value?.trim() || 'expeditionup@gmail.com';
  if (raw.toLowerCase() === 'none') return [];
  return raw.split(',').map((e) => e.trim().toLowerCase()).filter((e) => e.includes('@'));
}

export class GoogleSignIn {
  constructor(settings, fetchImpl = globalThis.fetch, now = Date.now) {
    this.settings = settings; this.fetchImpl = fetchImpl; this.now = now;
  }
  static fromEnv(env) {
    const clientId = env.GOOGLE_SIGNIN_CLIENT_ID?.trim(), clientSecret = env.GOOGLE_SIGNIN_CLIENT_SECRET?.trim();
    if (!clientId || !clientSecret) return undefined;
    const site = (env.SITE_URL?.trim() || 'https://www.lineofblue.co.uk').replace(/\/$/, '');
    return new GoogleSignIn({ clientId, clientSecret, redirectUri: env.GOOGLE_SIGNIN_REDIRECT_URI?.trim() || `${site}/login/google/callback` });
  }
  start() {
    const flow = { state: randomBytes(18).toString('base64url'), nonce: randomBytes(18).toString('base64url'), verifier: randomBytes(32).toString('base64url'), expires: this.now() + 10 * 60_000 };
    const q = new URLSearchParams({
      response_type: 'code', client_id: this.settings.clientId, redirect_uri: this.settings.redirectUri,
      scope: 'openid email profile', state: flow.state, nonce: flow.nonce,
      code_challenge: createHash('sha256').update(flow.verifier).digest('base64url'), code_challenge_method: 'S256', prompt: 'select_account',
    });
    return { flow, url: `${GOOGLE_AUTHORIZE}?${q}` };
  }
  async finish(flow, query) {
    if (query.error) throw new Error('Google sign-in was cancelled.');
    if (!flow || flow.expires < this.now() || !query.state || query.state !== flow.state) throw new Error('That Google sign-in has expired or was not started here. Please try again.');
    if (!query.code) throw new Error('Google did not return a sign-in code. Please try again.');
    const res = await this.fetchImpl(GOOGLE_TOKEN, {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ grant_type: 'authorization_code', code: query.code, redirect_uri: this.settings.redirectUri, client_id: this.settings.clientId, client_secret: this.settings.clientSecret, code_verifier: flow.verifier }).toString(),
      signal: AbortSignal.timeout(15_000),
    });
    if (!res.ok) throw new Error(`Google sign-in failed (${res.status}). Please try again.`);
    const claims = decodeJwtPayload((await res.json())?.id_token);
    if (!claims) throw new Error('Google sign-in failed: no identity came back.');
    const aud = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
    if (!ISSUERS.has(String(claims.iss)) || !aud.includes(this.settings.clientId)) throw new Error('Google sign-in failed: the identity was not for this site.');
    if (typeof claims.exp !== 'number' || claims.exp * 1000 < this.now()) throw new Error('Google sign-in failed: the identity has expired. Please try again.');
    if (claims.nonce !== flow.nonce) throw new Error('Google sign-in failed: please try again.');
    if (claims.email_verified !== true && claims.email_verified !== 'true') throw new Error("Your Google account's email isn't verified, so it can't be used to sign in.");
    const email = typeof claims.email === 'string' ? claims.email.trim().toLowerCase() : '';
    if (!email.includes('@')) throw new Error('Google did not share an email address.');
    return { email, name: typeof claims.name === 'string' ? claims.name : email };
  }
}
export function decodeJwtPayload(token) {
  if (typeof token !== 'string') return undefined;
  try { const p = JSON.parse(Buffer.from(token.split('.')[1] ?? '', 'base64url').toString('utf8')); return p && typeof p === 'object' ? p : undefined; }
  catch { return undefined; }
}
export const encodeFlow = f => [f.state, f.nonce, f.verifier, f.expires].join('|');
export function decodeFlow(raw) {
  const [state, nonce, verifier, exp] = String(raw || '').split('|'); const expires = Number(exp);
  return state && nonce && verifier && Number.isFinite(expires) ? { state, nonce, verifier, expires } : undefined;
}
