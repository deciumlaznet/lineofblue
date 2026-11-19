"""Usage: python ingest/telegram/run.py [--source TS-01] [--dry-run] [--status]
Caps (env, optional): TELEGRAM_DAILY_MESSAGE_CAP (default 2000).
Pseudonym salt: TELEGRAM_PSEUDONYM_SALT, or X_PSEUDONYM_SALT if that is not set."""
import asyncio, json, os, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from connector import Budget, CapError, approved, collect, load_sources  # noqa: E402

args = sys.argv[1:]
dry = "--dry-run" in args
out_dir = os.environ.get("LOB_INGEST_DIR") or os.path.join(HERE, "..", "..", "data", "ingest")
budget = Budget(os.path.join(out_dir, "telegram-ledger-dryrun.json" if dry else "telegram-ledger.json"), int(os.environ.get("TELEGRAM_DAILY_MESSAGE_CAP", 2000)))
if "--status" in args:
    print(json.dumps(budget.summary())); sys.exit(0)

sources = load_sources(os.path.join(HERE, "sources.json"))
if dry:
    sources = [dict(s, status="approved") for s in sources]
want = args[args.index("--source") + 1] if "--source" in args else None
sources = [s for s in approved(sources) if not want or s["id"] == want]
if not sources:
    print("No approved source to run. Approve one in ingest/telegram/sources.json."); sys.exit(2)
salt = "dry-run-salt-0000" if dry else (os.environ.get("TELEGRAM_PSEUDONYM_SALT") or os.environ.get("X_PSEUDONYM_SALT"))
state_path = os.path.join(out_dir, "telegram-state-dryrun.json" if dry else "telegram-state.json")
state = json.load(open(state_path)) if os.path.exists(state_path) else {}
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, f"telegram-{datetime.now(timezone.utc):%Y-%m-%d}{'-dryrun' if dry else ''}.jsonl")


async def main():
    if dry:
        fixture = json.load(open(os.path.join(HERE, "fixture.json")))

        async def fetch(source, limit, since):
            return fixture[:limit]
        c = None
    else:
        from live import client, make_fetch
        c = client(); await c.connect()
        if not await c.is_user_authorized():
            print("TELEGRAM_SESSION is missing or expired. Run ingest/telegram/login.py first."); return
        fetch = make_fetch(c)
    try:
        for s in sources:
            try:
                posts = await collect(s, fetch, budget, salt, state)
                with open(out, "a") as f:
                    f.writelines(json.dumps(p, ensure_ascii=False) + "\n" for p in posts)
                print(f"{s['id']}: {len(posts)} posts kept -> {out}")
            except CapError as e:
                print(f"{s['id']}: {e}"); break
            except Exception as e:  # one bad source must not stop the rest, except a flood wait
                print(f"{s['id']}: {e}")
                if "wait" in str(e): break
    finally:
        json.dump(state, open(state_path, "w"))
        if c: await c.disconnect()
    print(json.dumps(budget.summary()))

asyncio.run(main())
