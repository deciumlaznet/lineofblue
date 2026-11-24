# Private site: sign-in with two-factor, hosting and domain

The whole site is private. Every page, including the splash, the demo and the research page, needs a signed-in
session. Signing in takes a password and then a 6-digit code from an authenticator app (Google Authenticator,
Microsoft Authenticator, 1Password and similar), or one of ten single-use recovery codes.

Code: `web/` (Node, two packages: `pg` and `qrcode`). Tests: `node --test web/test.mjs`.

## Pages

| Path | Open to | What |
|---|---|---|
| `/login`, `/login/code` | everyone | Password, then authenticator code |
| `/login/google` | everyone | Sign in with Google (when set up) |
| `/setup` | only while no account exists, and only with the setup code | Creates the first account |
| `/robots.txt`, `/healthz` | everyone | Disallow all; health check |
| `/` | signed in | Splash (the line links to `/demo`) |
| `/demo` | signed in | `dist/index.html` |
| `/research` | signed in | `dist/research.html` |
| `/logout` | everyone | Sign out |

## Sign in with Google

Optional, alongside password and code (tester accounts and automated tests keep using those). Google only proves who
someone is: it signs in the account with that email, or an `ADMIN_EMAILS` address (default `expeditionup@gmail.com`).
An admin email with no account yet gets one on first Google sign-in, reachable only through Google; that also closes
`/setup`. Anyone else is refused and no account is made.

- Secrets: `GOOGLE_SIGNIN_CLIENT_ID`, `GOOGLE_SIGNIN_CLIENT_SECRET` (the shared OAuth client). Optional `ADMIN_EMAILS`,
  `SITE_URL` (default `https://www.lineofblue.co.uk`).
- Add `https://www.lineofblue.co.uk/login/google/callback` to the client's authorised redirect URIs.
- OpenID Connect code flow with PKCE, state and nonce; the ID token's issuer, audience, expiry, nonce and verified email
  are checked. Google accounts use Google's own two-step verification instead of the authenticator code.

## Safeguards

- Passwords hashed with scrypt (N=32768). Minimum 12 characters.
- Authenticator codes: RFC 6238, one 30-second step of clock drift allowed, each code usable once.
- Recovery codes stored only as hashes, each usable once.
- Five wrong passwords or codes lock the account for 15 minutes. Sign-in posts are also limited per address.
- Wrong email and wrong password give the same answer and take the same time.
- Sessions last 12 hours. Cookies are HttpOnly, Secure, SameSite=Lax and `__Host-` prefixed on https. Only a hash of
  each session token is stored.
- Forms posted from another site are refused. Pages cannot be framed. `noindex` on every response.
- `/setup` closes for good once the first account exists.

## Replit

- Secrets: `DATABASE_URL` (Replit Postgres, provided), `LOB_SETUP_CODE` (a phrase the owner chooses, needed once to
  create the first account; can be deleted afterwards).
- Tables `lob_users`, `lob_sessions`, `lob_setups` are created on start.
- Publish (Autoscale): build `cd lob && (git pull --ff-only origin main || true) && bash scripts/deploy_build.sh`,
  run `cd lob && NODE_ENV=production node web/server.mjs`, port 5000.

## Domain

`www.lineofblue.co.uk` and `lineofblue.co.uk` point at the Replit deployment through the records Replit shows under
Deployments, Settings, Link a domain (an A record and a TXT verification record for each name). DNS is at Porkbun.
The Resend records for `mail.lineofblue.co.uk` are separate and must not be changed.
