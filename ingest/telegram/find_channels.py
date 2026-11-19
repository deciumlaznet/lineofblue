"""Find candidate public Telegram channels to watch. Run in the Replit shell:
    python ingest/telegram/find_channels.py            (uses the default UK search terms below)
    python ingest/telegram/find_channels.py "uk news" "small boats"

Telegram's keyword search only covers channels an account has joined, so the connector needs a shortlist of
public broadcast channels. This script asks Telegram's directory search for channels whose name matches each
term and prints them biggest first. It does not join, follow or post anything. Groups and private chats are
skipped. Nothing is added to sources.json: a person picks from the list and approves each channel (W1.1).
Results are saved to data/ingest/telegram-candidates.json."""
import asyncio, json, os, re, sys
from pathlib import Path

TERMS = ["britain news", "british news", "england news", "great britain", "british patriots", "english patriots",
         "london news", "manchester news", "birmingham news", "scotland news", "welsh news", "small boats",
         "british politics", "unite the kingdom", "british police", "uk news", "uk protests", "fact check uk"]

# "uk" also matches "Ukraine" and "Ukrposhta": drop those, and titles mostly in Cyrillic.
OFF_TOPIC = re.compile(r"ukrain|ukr\b|ukrp|украин|україн|new south wales|kitesurf|crypto|nft", re.I)


def off_topic(title, username):
    cyr = sum(1 for ch in title if "\u0400" <= ch <= "\u04ff")
    return bool(OFF_TOPIC.search(f"{title} {username}")) or cyr > len(title) / 3


def shortlist(found):
    """found: list of (term, chat dict). Keep public broadcast channels, one row each, largest first."""
    rows = {}
    for term, ch in found:
        if not ch.get("broadcast") or not ch.get("username") or off_topic(ch.get("title", ""), ch["username"]):
            continue
        r = rows.setdefault(ch["username"].lower(), {"channel": ch["username"], "title": ch.get("title", ""),
                                                     "subscribers": ch.get("subscribers") or 0, "terms": []})
        if term not in r["terms"]:
            r["terms"].append(term)
    return sorted(rows.values(), key=lambda r: -r["subscribers"])


def proposed_sources(rows, start=1):
    return [{"id": f"TC-{i:02d}", "mode": "channel", "label": r["title"][:60], "channel": r["channel"],
             "status": "proposed", "maxPerRun": 50} for i, r in enumerate(rows, start)]


async def main(terms):
    from telethon.tl.functions.contacts import SearchRequest
    from live import client
    found = []
    async with client() as c:
        for t in terms:
            res = await c(SearchRequest(q=t, limit=20))
            for ch in res.chats:
                found.append((t, {"broadcast": getattr(ch, "broadcast", False), "username": getattr(ch, "username", None),
                                  "title": getattr(ch, "title", ""), "subscribers": getattr(ch, "participants_count", None)}))
            await asyncio.sleep(2)  # be gentle with Telegram's rate limits
    rows = shortlist(found)
    out = Path(__file__).resolve().parents[2] / "data" / "ingest"
    out.mkdir(parents=True, exist_ok=True)
    (out / "telegram-candidates.json").write_text(json.dumps({"terms": terms, "candidates": rows}, indent=1, ensure_ascii=False))
    print(f"{len(rows)} public channels found. Biggest first:\n")
    for i, r in enumerate(rows, 1):
        print(f"{i:>3}. {r['channel']:<32} {r['subscribers']:>9,}  {r['title'][:50]}  [{', '.join(r['terms'])}]")
    print(f"\nSaved to {out / 'telegram-candidates.json'}. Nothing has been joined or added to sources.json.")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    asyncio.run(main(sys.argv[1:] or TERMS))
