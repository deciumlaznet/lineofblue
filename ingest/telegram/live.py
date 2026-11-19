"""Live Telegram fetch with Telethon. Needs the Replit secrets TELEGRAM_API_ID, TELEGRAM_API_HASH and
TELEGRAM_SESSION (made once by login.py)."""
import asyncio, os
from datetime import datetime, timedelta, timezone


def client():
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    return TelegramClient(StringSession(os.environ["TELEGRAM_SESSION"]), int(os.environ["TELEGRAM_API_ID"]), os.environ["TELEGRAM_API_HASH"])


def _plain(msg, chat):
    return {"id": msg.id, "channel_id": chat.id, "date": msg.date.astimezone(timezone.utc).isoformat(),
            "text": msg.message or "", "views": msg.views, "forwards": msg.forwards,
            "broadcast": bool(getattr(chat, "broadcast", False)), "public": bool(getattr(chat, "username", None))}


def make_fetch(c):
    from telethon import errors
    from telethon.tl.functions.messages import SearchGlobalRequest
    from telethon.tl.types import InputMessagesFilterEmpty, InputPeerEmpty

    async def fetch(source, limit, since):
        try:
            if source["mode"] == "search":
                since_dt = datetime.fromisoformat(since) if since else datetime.now(timezone.utc) - timedelta(days=2)
                res = await c(SearchGlobalRequest(q=source["query"], filter=InputMessagesFilterEmpty(), min_date=since_dt, max_date=None,
                                                  offset_rate=0, offset_peer=InputPeerEmpty(), offset_id=0, limit=limit, broadcasts_only=True))
                chats = {ch.id: ch for ch in res.chats}
                return [_plain(m, chats[m.peer_id.channel_id]) for m in res.messages if getattr(m.peer_id, "channel_id", None) in chats]
            entity = await c.get_entity(source["channel"])
            if not getattr(entity, "broadcast", False):
                raise ValueError(f"{source['id']}: {source['channel']} is not a broadcast channel; groups are not read.")
            return [_plain(m, entity) async for m in c.iter_messages(entity, limit=limit, min_id=since or 0)]
        except errors.FloodWaitError as e:
            raise RuntimeError(f"Telegram asked us to wait {e.seconds} s. Stopping this run.") from e
    return fetch
