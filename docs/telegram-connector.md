# Telegram connector

The connector reads public Telegram broadcast channels for the same eight topics as the X connector, and writes the results in Line of Blue's post shape. It never reads groups, private chats or users. The Telegram app is "Decium Laznet Listening".

## First-time sign-in (once)

1. In the Replit shell, run `pip install telethon`, then `python ingest/telegram/login.py`.
2. Enter the phone number for the Telegram account. Telegram then sends a code to that phone. Type the code in.
3. The script prints a long session string. Save it as the Replit secret **TELEGRAM_SESSION**. That string gives full access to the account, so keep it only in Replit secrets.

## Run it

| Command | What it does |
|---|---|
| `python ingest/telegram/run.py --dry-run` | Runs against a built-in fixture. Needs no sign-in. |
| `python ingest/telegram/run.py` | Live run of every approved source. |
| `python ingest/telegram/run.py --status` | Shows the messages read today against the cap. |
| `python -m unittest ingest/telegram/test_connector.py` | Runs the tests. Needs no network. |

## Secrets and settings

| Name | Needed | Purpose |
|---|---|---|
| `TELEGRAM_API_ID`, `TELEGRAM_API_HASH` | yes | The app's keys (already added). |
| `TELEGRAM_SESSION` | yes | Created by `login.py`. |
| `TELEGRAM_PSEUDONYM_SALT` | no | Salt for pseudonyms. If it isn't set, the connector uses `X_PSEUDONYM_SALT`. |
| `TELEGRAM_DAILY_MESSAGE_CAP` | no, default 2000 | The most messages read in a UTC day. |

Telegram is free to use. The cap stops the account being limited for reading too much. Each source reads at most 50 messages per run. If Telegram asks the connector to wait (`FLOOD_WAIT`), the run stops.

## Safeguards

- **Approved sources only.** Sources live in `ingest/telegram/sources.json` and run only when the NPCC Comms lead marks them `approved`. The eight keyword searches are `proposed`.
- **Public broadcast channels only.** Search results are limited to broadcast channels. Messages from anything without a public username are dropped. Channel sources must be broadcast channels, never groups.
- **Searches never target an account.** A search may not name an account (`@...`) or a `t.me` link.
- **What is stored.** Channels and message IDs are replaced by salted pseudonyms, and handles and `t.me` links are removed from the text. No one is ever looked up. Only the text, time, views and forwards are kept.
- **Channel sources keep matching messages only.** When a channel is read, only messages that match its keywords are kept. The rest are dropped without being stored.
