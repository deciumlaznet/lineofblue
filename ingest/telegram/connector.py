"""Line of Blue: Telegram connector (public broadcast channels only).

Narrative-first, like the X connector:
- runs approved keyword searches across public channels, and reads an approved list of public channels;
- never reads private chats, groups or users, and never looks up who is behind a channel;
- pseudonymises every channel before anything is stored, and scrubs handles and links from text;
- caps the messages read per source per run and per day, and stops when Telegram asks it to wait.

The Telegram client (Telethon) is imported only for live runs, so the tests need no sign-in.
"""
import hashlib, hmac, json, os, re
from datetime import datetime, timezone

HANDLE = re.compile(r"@\w{3,32}")
TME = re.compile(r"(https?://)?(t\.me|telegram\.me)/[\w+/-]+", re.I)


class CapError(Exception):
    pass


# ------------------------------------------------------------------ budget
class Budget:
    """Counts messages read per UTC day. Telegram is free, but heavy reading gets an account limited,
    so the cap protects the account rather than a bill."""

    def __init__(self, path, daily_cap, now=lambda: datetime.now(timezone.utc)):
        self.path, self.daily_cap, self.now = path, daily_cap, now
        self.ledger = json.load(open(path)) if os.path.exists(path) else {"days": {}}

    def _day(self):
        return self.now().strftime("%Y-%m-%d")

    def used(self):
        return self.ledger["days"].get(self._day(), 0)

    def allowance(self, want):
        return max(0, min(want, self.daily_cap - self.used()))

    def record(self, n):
        d = self._day()
        self.ledger["days"][d] = self.ledger["days"].get(d, 0) + n
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        json.dump(self.ledger, open(self.path, "w"), indent=1)

    def summary(self):
        return {"readToday": self.used(), "dailyCap": self.daily_cap}


# ------------------------------------------------------------------ privacy
def pseudonym(kind, raw_id, salt):
    if not salt or len(salt) < 16:
        raise ValueError("A pseudonym salt (16+ characters) must be set before any live run.")
    return f"{kind}_" + hmac.new(salt.encode(), f"tg:{raw_id}".encode(), hashlib.sha256).hexdigest()[:10]


def scrub(text):
    return TME.sub("[link]", HANDLE.sub("@user", text or ""))


def to_post(m, source, salt):
    """m: a plain dict made from a Telegram message (see live.py)."""
    return {
        "id": pseudonym("T", f"{m['channel_id']}/{m['id']}", salt),
        "narrative": None, "set": source["id"], "platform": "telegram", "source": "telegram-" + source["mode"],
        "synthetic": False, "t": m["date"], "account": pseudonym("chan", m["channel_id"], salt), "place": None,
        "text": scrub(m["text"]), "lang": "und", "reach": m.get("views") or 0, "shares": m.get("forwards") or 0, "flags": [],
    }


def keep(m, source):
    """Only public broadcast channels, only messages with text, and for channel sources only messages
    that match the source's keywords (the rest are dropped unread, never stored)."""
    if not m.get("broadcast") or not m.get("public") or not (m.get("text") or "").strip():
        return False
    kws = source.get("keywords") or []
    return not kws or any(k.lower() in m["text"].lower() for k in kws)


# ------------------------------------------------------------------ sources
def load_sources(path):
    cfg = json.load(open(path))
    for s in cfg["sources"]:
        if s["mode"] not in ("search", "channel"):
            raise ValueError(f"{s['id']}: mode must be search or channel")
        if s["mode"] == "search" and ("@" in s["query"] or "t.me" in s["query"]):
            raise ValueError(f"{s['id']}: searches may not target accounts or channels")
        if s["mode"] == "channel" and not re.fullmatch(r"[A-Za-z]\w{3,31}", s.get("channel", "")):
            raise ValueError(f"{s['id']}: channel must be a public channel username")
    return cfg["sources"]


def approved(sources):
    return [s for s in sources if s.get("status") == "approved"]


# ------------------------------------------------------------------ run
async def collect(source, fetch, budget, salt, state):
    """fetch(source, limit, since) -> list of message dicts. state holds the last id seen per source."""
    if source.get("status") != "approved":
        raise CapError(f"{source['id']} is \"{source.get('status')}\". Only approved sources can run.")
    n = budget.allowance(source.get("maxPerRun", 50))
    if n <= 0:
        raise CapError(f"Daily cap reached: {budget.summary()}")
    msgs = await fetch(source, n, state.get(source["id"]))
    budget.record(len(msgs))
    if msgs:
        state[source["id"]] = max(m["id"] for m in msgs) if source["mode"] == "channel" else max(m["date"] for m in msgs)
    return [to_post(m, source, salt) for m in msgs if keep(m, source)]
