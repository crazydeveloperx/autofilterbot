import logging
import logging.config

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)
from pyromod import listen

from pyrogram import Client
from database.db import db
from info import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, SUPPORT_GROUP, PORT
from utils import temp, get_time, restart_clone_bot
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from pyrogram.errors import FloodWait, UserIsBlocked, AccessTokenExpired, AccessTokenInvalid
import asyncio
import datetime
from pyromod import listen
import time
import pytz
from datetime import datetime
from aiohttp import web
from plugins import web_server

class Bot(Client):
    def __init__(self):
        super().__init__(
            name='Auto_Filter_Bot',
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        temp.BOT = self
        temp.CRAZY = self
        temp.BOT_USERNAME = me.username
        temp.BOT_NAME = me.first_name
        temp.BOT_ID = me.id
        temp.BOT_START_TIME = time.time()
        print(f"\n@{me.username} Is Started Now 🥰\n")

       # bots = await db.get_all_bots()
#for bot in bots:
       #     asyncio.create_task(restart_clone_bot(bot))
        print("Successfully restarted all bots.")
        #await self.send_message(LOG_CHANNEL, text=f"<b>{me.mention} Is Restarted ✅️</b>")
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        print("Bot Is Stopped!")

    async def iter_messages(self: Client, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially.
        This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
        you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
        single call.
        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).
                
            limit (``int``):
                Identifier of the last message to be returned.
                
            offset (``int``, *optional*):
                Identifier of the first message to be returned.
                Defaults to 0.
        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        Example:
            .. code-block:: python
                async for message in app.iter_messages("pyrogram", 1000, 100):
                    print(message.text)
        """
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1


app = Bot()
app.run()
