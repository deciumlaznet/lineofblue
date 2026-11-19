# X connector

The connector reads public posts from X recent search, using keyword sets about topics, and turns them into Line of Blue's post shape. It is the first live source for Narrative Radar and Trend watch. Account: @DeciumLaznet, on X's pay-per-use plan.

## Run it

| Command | What it does |
|---|---|
| `node ingest/x/run.mjs --dry-run` | Runs every set against a built-in fixture. No network, no credit. |
| `node ingest/x/run.mjs --set XS-01` | Live run of one approved set. |
| `node ingest/x/run.mjs --status` | Shows posts read today and this month, and the estimated spend. |
| `node --test ingest/x/test.mjs` | The connector's tests. They need no network. |

Output goes to `data/ingest/x-YYYY-MM-DD.jsonl`, one post per line. That folder is git-ignored.

## Secrets and settings (Replit secrets)

| Name | Needed | Purpose |
|---|---|---|
| `X_BEARER_TOKEN` | yes | The app's bearer token. |
| `X_PSEUDONYM_SALT` | yes | Any random string of 16 or more characters. It salts the pseudonyms. Keep it secret and never change it, or the same account will get a new pseudonym. |
| `X_DAILY_POST_CAP` | no, default 100 | The most posts read in a UTC day. |
| `X_MONTHLY_POST_CAP` | no, default 3000 | The most posts read in a month. At about $0.005 a post, that is about $15 a month (agreed 19 Nov 2026). |
| `X_PRICE_PER_POST_USD` | no, default 0.005 | Used only for the spend estimate. |
| `LOB_INGEST_DIR` | no | Where output and the ledger are written. |

## How spending is capped

X bills for every post it returns. Before each request, the connector works out how many posts the caps still allow. It sets `max_results` to that number, or sends no request at all if fewer than 10 remain. Each post it reads is recorded in `x-ledger.json`. A run that hits a cap stops straight away. Set a matching spend limit in the X developer console as a second line of defence.

Replit's file system can reset when the app is redeployed, and the ledger would reset with it. Before running on a schedule, move the ledger into the Replit database.

## Safeguards (narrative-first)

- **Approved sets only.** Keyword sets live in `ingest/x/queries.json`. A set runs only when the NPCC Comms lead changes its status to `approved` (workflow step W1.1). All eight sets were approved on 19 Nov 2026. Each takes up to 12 posts a run, so one run of all eight fits inside the daily cap of 100.
- **No account targeting.** Sets that use `from:`, `to:`, `mentions:`, `retweets_of:` or `@handle` are refused when the file loads.
- **No identities stored.** No user lookups are requested. Each author ID is replaced by a salted HMAC pseudonym, and so is each post ID. Handles and profile links are removed from the post text.
- **What is kept.** Text, language, time, impressions, and shares (reposts plus quotes). Location is not kept.
- **Retention.** Proposed: 30 days for post text, then keep only aggregates. This needs a decision before any police use.
