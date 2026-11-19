"""Search-term tuning for Telegram. Reads the latest messages from candidate public channels and scores how
much of each channel is about our topics, so a person can choose which channels to watch.
    python ingest/telegram/sample_channels.py                 (top 25 from data/ingest/telegram-candidates.json)
    python ingest/telegram/sample_channels.py chanA chanB     (named public channels)
    python ingest/telegram/sample_channels.py --snowball      (channels the last sample forwarded from, not yet sampled)
Also lists the public channels that the sampled channels forward from most ("snowball"), which is how
related channels are usually found. Reads only; joins nothing. Messages are scored in memory: the report keeps counts and up to 3 scrubbed
example lines per channel, nothing else. Saved to data/ingest/telegram-channel-sample.json."""
import asyncio, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from connector import scrub  # noqa: E402

TOPICS = {
    "fake notices": ["fake police", "curfew", "police notice", "police letter", "hoax"],
    "spiking": ["spiked", "spiking"],
    "scam fines": ["penalty notice", "speeding fine", "pcn", "police fine"],
    "suspect rumours": ["named as", "real name", "won't name", "refuse to name", "suspect", "stabbing", "attacker"],
    "cover-up": ["cover up", "cover-up", "covering up", "media blackout", "hiding the truth", "police lied"],
    "gatherings": ["asylum hotel", "migrant hotel", "be there", "take to the streets", "protest", "mosque"],
    "old footage": ["old footage", "old video", "years ago", "not from today"],
    "fake statements": ["fake statement", "doctored", "photoshopped", "fake screenshot"],
}
UK = re.compile(r"\b(uk|britain|british|england|english|scotland|wales|london|manchester|birmingham|leeds|liverpool|glasgow|"
                r"police|constabulary|met police|home office|starmer|reform)\b", re.I)
N_MESSAGES = 40


def score(texts):
    """texts: list of message strings from one channel -> topic counts, UK share, examples."""
    hits, uk, examples = {k: 0 for k in TOPICS}, 0, []
    for t in texts:
        low = t.lower(); matched = [k for k, words in TOPICS.items() if any(w in low for w in words)]
        for k in matched:
            hits[k] += 1
        uk += bool(UK.search(t))
        if matched and len(examples) < 3:
            examples.append({"topics": matched, "text": scrub(t)[:240]})
    n = len(texts) or 1
    on_topic = sum(1 for t in texts if any(w in t.lower() for ws in TOPICS.values() for w in ws))
    return {"messages": len(texts), "onTopicShare": round(on_topic / n, 2), "ukShare": round(uk / n, 2),
            "topics": {k: v for k, v in hits.items() if v}, "examples": examples}


async def main(names):
    from live import client
    from telethon.tl.types import PeerChannel
    rows, fwd = [], {}
    async with client() as c:
        for name in names:
            try:
                ent = await c.get_entity(name)
                if not getattr(ent, "broadcast", False):
                    rows.append({"channel": name, "skipped": "not a broadcast channel"}); continue
                msgs = [m async for m in c.iter_messages(ent, limit=N_MESSAGES)]
                texts = [m.message for m in msgs if m.message]
                for m in msgs:
                    cid = getattr(getattr(m.fwd_from, "from_id", None), "channel_id", None) if m.fwd_from else None
                    if cid and cid != ent.id:
                        fwd[cid] = fwd.get(cid, 0) + 1
                rows.append({"channel": name, "title": getattr(ent, "title", ""), **score(texts)})
            except Exception as e:  # noqa: BLE001 - one bad channel must not stop the rest
                rows.append({"channel": name, "skipped": str(e)[:120]})
            await asyncio.sleep(2)
        sources = []
        for cid, n in sorted(fwd.items(), key=lambda kv: -kv[1])[:20]:
            try:
                e = await c.get_entity(PeerChannel(cid))
                if getattr(e, "username", None) and getattr(e, "broadcast", False):
                    sources.append({"channel": e.username, "title": getattr(e, "title", ""), "forwardedTimes": n})
            except Exception:  # noqa: BLE001 - private or unknown to this account
                pass
    rows.sort(key=lambda r: -(r.get("onTopicShare", 0) + r.get("ukShare", 0)))
    out = Path(__file__).resolve().parents[2] / "data" / "ingest"
    out.mkdir(parents=True, exist_ok=True)
    hist = out / "telegram-sampled.json"
    seen = json.loads(hist.read_text()) if hist.exists() else {}
    for r in rows:
        if "messages" in r:
            seen[r["channel"]] = {k: r[k] for k in ("title", "onTopicShare", "ukShare", "topics")}
    hist.write_text(json.dumps(seen, indent=1, ensure_ascii=False))
    (out / "telegram-channel-sample.json").write_text(json.dumps({"channels": rows, "forwardedFrom": sources}, indent=1, ensure_ascii=False))
    for r in rows:
        print(f"{r['channel']:<30} " + (f"on-topic {r['onTopicShare']:.0%}  UK {r['ukShare']:.0%}  {r['topics']}" if "messages" in r else r["skipped"]))
    print("\nMost forwarded-from public channels (candidates for the next sample):")
    for f in sources:
        print(f"  {f['channel']:<30} x{f['forwardedTimes']}  {f['title'][:50]}")
    print(f"\nSaved to {out / 'telegram-channel-sample.json'}.")


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    data = Path(__file__).resolve().parents[2] / "data" / "ingest"
    if "--snowball" in sys.argv:
        last, hist = data / "telegram-channel-sample.json", data / "telegram-sampled.json"
        seen = json.loads(hist.read_text()) if hist.exists() else {}
        prev = json.loads(last.read_text()).get("forwardedFrom", []) if last.exists() else []
        names = [f["channel"] for f in prev if f["channel"] not in seen][:25]
        if not names:
            print("Snowball: no new channels to sample."); sys.exit(0)
    if not names:
        f = Path(__file__).resolve().parents[2] / "data" / "ingest" / "telegram-candidates.json"
        names = [r["channel"] for r in json.loads(f.read_text())["candidates"][:25]]
    asyncio.run(main(names))
