"""Usage: python ingest/news/run.py [--source NS-BBC-UK] [--check] [--dry-run]
  --check    fetch every source once and report whether it works and how many items it has (stores nothing)
  --dry-run  use the offline fixture instead of the internet
Writes new stories to data/ingest/news-YYYY-MM-DD.jsonl; remembers what it has seen in news-seen.json."""
import json, sys, time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from connector import approved, collect, load_sources  # noqa: E402

here, root = Path(__file__).parent, Path(__file__).resolve().parents[2]
args = sys.argv[1:]
dry, check = "--dry-run" in args, "--check" in args
want = args[args.index("--source") + 1] if "--source" in args else None
sources = [s for s in (load_sources(here / "sources.json") if check else approved(load_sources(here / "sources.json"))) if not want or s["id"] == want]
fixture = json.loads((here / "fixture.json").read_text())


def get(url):
    if not dry:
        from connector import http_get
        return http_get(url)
    key = "gdelt" if "gdeltproject" in url else "rss"
    return fixture[key].encode()


out = root / "data" / "ingest"
out.mkdir(parents=True, exist_ok=True)
seen_file = out / ("news-seen-dryrun.json" if dry else "news-seen.json")
seen = set(json.loads(seen_file.read_text())) if seen_file.exists() and not check else set()
dest = out / f"news-{date.today().isoformat()}{'-dryrun' if dry else ''}.jsonl"
total = 0
for s in sources:
    try:
        posts, n = collect(s, get, set() if check else seen)
        if check:
            print(f"OK    {s['id']:<17} {n:>3} items, {len(posts):>3} kept  {s['publisher']}")
        else:
            with dest.open("a") as f:
                for p in posts:
                    f.write(json.dumps(p, ensure_ascii=False) + "\n")
            total += len(posts)
            print(f"{s['id']}: {len(posts)} new stories")
    except Exception as e:  # noqa: BLE001 - one broken feed must not stop the rest
        print(f"{'FAIL ' if check else ''}{s['id']}: {str(e)[:160]}")
    time.sleep(0 if dry else 1)  # be polite to publishers
if not check:
    seen_file.write_text(json.dumps(sorted(seen)))
    print(f"{total} new stories -> {dest}")
