// Sign-in pages. Black ground and the brand blue (docs/brand.md), no scripts, no outside fonts.
export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const CSS = `
:root { --ground:#000; --ink:#3d9bff; --text:#e8eef7; --muted:#8b98ab; --line:#1f2a3a; --bad:#ff7a7a; color-scheme: dark; }
* { box-sizing: border-box; }
html, body { margin: 0; min-height: 100%; background: var(--ground); color: var(--text);
  font: 16px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
main { max-width: 380px; margin: 0 auto; padding: 14vh 16px 48px; }
.rule { height: 2px; background: var(--ink); margin: 0 0 28px; border-radius: 1px; }
h1 { font-size: 18px; font-weight: 600; margin: 0 0 4px; letter-spacing: .01em; }
p { margin: 0 0 16px; color: var(--muted); font-size: 14px; }
label { display: block; font-size: 13px; color: var(--muted); margin: 14px 0 6px; }
input { width: 100%; padding: 11px 12px; background: #0a0f16; color: var(--text); border: 1px solid var(--line);
  border-radius: 6px; font: inherit; }
input:focus { outline: 2px solid var(--ink); outline-offset: 1px; border-color: transparent; }
input.code { font: 600 22px/1.2 ui-monospace, "SF Mono", Menlo, Consolas, monospace; letter-spacing: .3em; text-align: center; }
a.button { display: block; text-align: center; text-decoration: none; }
button, a.button { margin-top: 20px; width: 100%; padding: 11px 12px; background: var(--ink); color: #00101f; border: 0;
  border-radius: 6px; font: 600 15px/1.2 inherit; font-family: inherit; cursor: pointer; }
button:focus-visible, a.button:focus-visible { outline: 2px solid var(--text); outline-offset: 2px; }
.err { color: var(--bad); font-size: 14px; margin: 12px 0 0; }
.qr { background: #fff; padding: 12px; border-radius: 8px; width: 220px; margin: 8px auto 12px; display: block; }
.secret, .codes { font: 14px/1.7 ui-monospace, "SF Mono", Menlo, Consolas, monospace; color: var(--text);
  background: #0a0f16; border: 1px solid var(--line); border-radius: 6px; padding: 10px 12px; word-break: break-all; }
.codes { columns: 2; }
a { color: var(--ink); }
.small { font-size: 13px; }
`;

export function page(title, body) {
  return `<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>${esc(title)} · Line of Blue</title>
<style>${CSS}</style>
</head>
<body><main><div class="rule" aria-hidden="true"></div>${body}</main></body>
</html>`;
}

const err = (e) => e ? `<p class="err" role="alert">${esc(e)}</p>` : '';

export const loginPage = (e, email = '') => page('Sign in', `
<h1>Sign in</h1>
<p>This site is private.</p>
<form method="post" action="/login" autocomplete="on">
  <label for="email">Email</label>
  <input id="email" name="email" type="email" autocomplete="username" required value="${esc(email)}" autofocus>
  <label for="password">Password</label>
  <input id="password" name="password" type="password" autocomplete="current-password" required>
  ${err(e)}
  <button type="submit">Continue</button>
</form>`);

export const codePage = (e) => page('Enter code', `
<h1>Enter your code</h1>
<p>Open your authenticator app and enter the 6-digit code for Line of Blue. Lost your phone? Enter one of your recovery codes instead.</p>
<form method="post" action="/login/code" autocomplete="off">
  <label for="code">Code</label>
  <input id="code" name="code" class="code" inputmode="numeric" autocomplete="one-time-code" required maxlength="20" autofocus>
  ${err(e)}
  <button type="submit">Sign in</button>
</form>
<p class="small" style="margin-top:20px"><a href="/login">Start again</a></p>`);

export const setupMissingPage = () => page('Set up', `
<h1>Set up the first account</h1>
<p>Setup is switched off. To switch it on, add a secret named <b>LOB_SETUP_CODE</b> in Replit Secrets, set to a phrase only you know, then publish again and reload this page.</p>`);

export const setupPage = (e, email = '') => page('Set up', `
<h1>Set up the first account</h1>
<p>Enter the setup code you saved as LOB_SETUP_CODE in Replit Secrets, then choose your sign-in details.</p>
<form method="post" action="/setup" autocomplete="off">
  <label for="setup">Setup code</label>
  <input id="setup" name="setup" type="password" required autofocus>
  <label for="email">Email</label>
  <input id="email" name="email" type="email" autocomplete="username" required value="${esc(email)}">
  <label for="password">Password (at least 12 characters)</label>
  <input id="password" name="password" type="password" autocomplete="new-password" minlength="12" required>
  <label for="password2">Password again</label>
  <input id="password2" name="password2" type="password" autocomplete="new-password" minlength="12" required>
  ${err(e)}
  <button type="submit">Next</button>
</form>`);

export const setupAppPage = (qrDataUrl, secret, e) => page('Add to authenticator', `
<h1>Add Line of Blue to your authenticator app</h1>
<p>In Google Authenticator, Microsoft Authenticator, 1Password or similar, add an account and scan this code.</p>
<img class="qr" src="${esc(qrDataUrl)}" alt="QR code for your authenticator app" width="220" height="220">
<p class="small">Can't scan? Enter this key by hand (time-based):</p>
<div class="secret">${esc(secret.replace(/(.{4})/g, '$1 ').trim())}</div>
<form method="post" action="/setup/confirm" autocomplete="off">
  <label for="code">Then enter the 6-digit code it shows</label>
  <input id="code" name="code" class="code" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9 ]{6,7}" required autofocus>
  ${err(e)}
  <button type="submit">Turn on two-factor sign-in</button>
</form>`);

export const recoveryPage = (codes) => page('Recovery codes', `
<h1>Save your recovery codes</h1>
<p>Each code signs you in once if you lose your phone. Store them somewhere safe, such as a password manager. They will not be shown again.</p>
<div class="codes">${codes.map((c) => `<div>${esc(c)}</div>`).join('')}</div>
<a class="button" href="/">I've saved them, continue</a>`);

export const logoutPage = () => page('Sign out', `
<h1>Sign out</h1>
<form method="post" action="/logout"><button type="submit">Sign out</button></form>
<p class="small" style="margin-top:20px"><a href="/">Back</a></p>`);

export const messagePage = (title, text) => page(title, `<h1>${esc(title)}</h1><p>${esc(text)}</p><p class="small"><a href="/login">Sign in</a></p>`);
