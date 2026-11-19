"""One-off sign-in. Run in the Replit shell:  python ingest/telegram/login.py
Telegram texts a code to the account's phone; type it here. The script prints a session string:
save it as the Replit secret TELEGRAM_SESSION. That string gives full access to the account, so it must
only ever live in Replit secrets, never in code, chat or the repo."""
import asyncio, os
from telethon import TelegramClient
from telethon.sessions import StringSession


async def main():
    async with TelegramClient(StringSession(), int(os.environ["TELEGRAM_API_ID"]), os.environ["TELEGRAM_API_HASH"]) as c:
        me = await c.get_me()
        print(f"Signed in. Save the line below as the Replit secret TELEGRAM_SESSION (account id ends ...{str(me.id)[-3:]}).\n")
        print(c.session.save())

asyncio.run(main())
