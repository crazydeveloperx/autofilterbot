from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from database.db import db
from utils import get_time
import re
from info import ADMINS
from typing import Union, Optional, AsyncGenerator
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from clone_database.files_db import save_clone_bot_file
import asyncio

class index_temp(object):
    IS_INDEXINGS = {}
    IS_CANCELS = {}

@Client.on_message(filters.private & filters.command('index') & filters.user(ADMINS))
async def start_index(client, message):
    me = await client.get_me()
    bot = await db.get_bot(me.id)
    settings = await db.get_bot_settings(me.id)
    if bot['_id'] != message.from_user.id:
        return await message.reply('ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪs ʙᴏᴛ 😑')
    if settings['mongodb'] == "":
        return await message.reply("❌ ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴍᴏɴɢᴏ ᴅʙ")
    indexing = index_temp.IS_INDEXINGS.get(message.from_user.id)
    if indexing:
        return await message.reply('ᴄᴜʀʀᴇɴᴛʟʏ ɪɴᴅᴇx ᴘʀᴏᴄᴇssɪɴɢ! ᴡᴀɪᴛ ꜰᴏʀ ᴄᴏᴍᴘʟᴇᴛᴇ ɪᴛ.')

    m = await message.reply("ꜰᴏʀᴡᴀʀᴅ ʟᴀsᴛ ᴍᴇssᴀɢᴇ ᴏʀ sᴇɴᴅ ʟᴀsᴛ ᴍᴇssᴀɢᴇ ʟɪɴᴋ.\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss.")
    msg = await client.listen(message.from_user.id)
    if msg.text == '/cancel':
        await m.delete()
        await message.reply("ᴄᴀɴᴄᴇʟᴇᴅ ᴛʜɪs ᴘʀᴏᴄᴇss...")
        return
    if msg.text and msg.text.startswith("https://t.me"):
        try:
            try:
                _, _, _, chat_id, msg_id = msg.text.split("/")
                last_msg_id = int(msg_id)
                if chat_id.isnumeric():
                    chat_id = int(("-100" + chat_id))
            except:
                _, _, _, _, chat_id, msg_id = msg.text.split("/")
                last_msg_id = int(msg_id)
                if chat_id.isnumeric():
                    chat_id = int(("-100" + chat_id))
        except:
            await m.delete()
            await message.reply('⚠️ ɪɴᴠᴀʟɪᴅ ᴍᴇssᴀɢᴇ ʟɪɴᴋ')
            return
    elif msg.forward_from_chat and msg.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = msg.forward_from_message_id
        chat_id = msg.forward_from_chat.username or msg.forward_from_chat.id
    else:
        await m.delete()
        await message.reply('💢 sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ')
        return
    await m.delete()
    try:
        chat = await client.get_chat(chat_id)
    except Exception as e:
        return await message.reply(f'Error - <code>{e}</code>')
    if chat.type != enums.ChatType.CHANNEL:
        return await message.reply("ɪ ᴄᴀɴ ɪɴᴅᴇx ᴏɴʟʏ ᴄʜᴀɴɴᴇʟs.")
    s = await message.reply('sᴇɴᴅ ᴍᴇ ᴀ sᴋɪᴘ ᴍᴇssᴀɢᴇ ɴᴜᴍʙᴇʀ...')
    msg = await client.listen(message.from_user.id)
    try:
        skip = int(msg.text)
    except:
        await s.delete()
        await message.reply('ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!!')
        return
    await s.delete()
    buttons = [[
        InlineKeyboardButton('ʏᴇs', callback_data=f'index#yes#{chat_id}#{last_msg_id}#{skip}')
    ],[
        InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data=f'index#close#{chat_id}#{last_msg_id}#{skip}')
    ]]
    await message.reply(f"<b>ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɪɴᴅᴇx <b>{chat.title}</b> ᴄʜᴀɴɴᴇʟ??</b>", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'^index'))
async def index_callback(bot, query):
    _, ident, chat, lst_msg_id, skip = query.data.split("#")
    if ident == 'yes':
        msg = query.message
        await msg.edit('✅ sᴛᴀʀᴛɪɴɢ ɪɴᴅᴇxɪɴɢ...')
        try:
            chat = int(chat)
        except:
            chat = chat
        index_temp.IS_INDEXINGS[query.from_user.id] = True
        await index_files(int(lst_msg_id), bot, chat, msg, int(skip), query.from_user.id)

    elif ident == 'close':
        await query.answer("Okay!")
        await query.message.delete()

    elif ident == 'cancel':
        await query.message.edit("ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ɪɴᴅᴇxɪɴɢ...")
        index_temp.IS_CANCELS[query.from_user.id] = True


async def index_files(lst_msg_id, bot, chat, msg, skip, user_id):
    me = await bot.get_me()
    index_temp.IS_CANCELS[user_id] = False
    fetched = skip
    total = lst_msg_id
    remaining = lst_msg_id - skip
    saved = 0
    duplicate = 0
    deleted = 0
    unsupported = 0
    start_time = time.time()

    try:
        async for message in iter_messages(bot, chat, lst_msg_id, skip):
            if index_temp.IS_CANCELS.get(user_id):
                break
            fetched += 1
            remaining -= 1
            if fetched % 30 == 0:
                btn = [[
                    InlineKeyboardButton('ᴄᴀɴᴄᴇʟ', callback_data=f'index#cancel#{chat}#{lst_msg_id}#{skip}')
                ]]
                await msg.edit_text(text=f"<b>📥 ɪɴᴅᴇx ᴘʀᴏᴄᴇssɪɴɢ...\n\nᴛᴏᴛᴀʟ ᴍᴇssᴀɢᴇs - <code>{total}</code>\nꜰᴇᴛᴄʜᴇᴅ ᴍᴇssᴀɢᴇs - <code>{fetched}</code>\nʀᴇᴍᴀɪɴɪɴɢ ᴍᴇssᴀɢᴇs - <code>{remaining}</code>\nᴛᴏᴛᴀʟ ꜰɪʟᴇs sᴀᴠᴇᴅ - <code>{saved}</code>\nᴅᴜᴘʟɪᴄᴀᴛᴇ ꜰɪʟᴇs sᴋɪᴘᴘᴇᴅ - <code>{duplicate}</code>\nᴅᴇʟᴇᴛᴇᴅ ᴍᴇssᴀɢᴇs sᴋɪᴘᴘᴇᴅ - <code>{deleted}</code>\nᴜɴsᴜᴘᴘᴏʀᴛᴇᴅ ꜰɪʟᴇs sᴋɪᴘᴘᴇᴅ - <code>{unsupported}</code></b>", reply_markup=InlineKeyboardMarkup(btn))
            if message.empty:
                deleted += 1
                await asyncio.sleep(0.1)
                continue
            elif not message.media:
                unsupported += 1
                continue
            elif message.media not in [enums.MessageMediaType.DOCUMENT, enums.MessageMediaType.VIDEO]:
                unsupported += 1
                continue
            media = getattr(message, message.media.value, None)
            if not media:
                unsupported += 1
                continue
            sts = await save_clone_bot_file(me.id, media)
            await asyncio.sleep(0.1)
            if sts == "Saved":
                saved += 1
            elif sts == "Duplicates":
                duplicate += 1
    except Exception as e:
        index_temp.IS_INDEXINGS[user_id] = False
        await msg.edit(f'<b>⚠️ ɪɴᴅᴇx ᴄᴀɴᴄᴇʟᴇᴅ!!\n\nᴛɪᴍᴇ ᴛᴀᴋᴇɴ - <code>{time_taken}</code>\n\nᴛᴏᴛᴀʟ ᴍᴇssᴀɢᴇs - <code>{total}</code>\nꜰᴇᴛᴄʜᴇᴅ ᴍᴇssᴀɢᴇs - <code>{fetched}</code>\nᴛᴏᴛᴀʟ sᴀᴠᴇᴅ ꜰɪʟᴇs - <code>{saved}</code>\nᴅᴜᴘʟɪᴄᴀᴛᴇ ꜰɪʟᴇs sᴋɪᴘᴘᴇᴅ - <code>{duplicate}</code>\nᴅᴇʟᴇᴛᴇᴅ ᴍᴇssᴀɢᴇs sᴋɪᴘᴘᴇᴅ - <code>{deleted}</code>\nᴜɴsᴜᴘᴘᴏʀᴛᴇᴅ ꜰɪʟᴇs sᴋɪᴘᴘᴇᴅ -<code>{unsupported}</code></b>')
        await msg.reply(f"⚠️ ɪɴᴅᴇx ᴄᴀɴᴄᴇʟᴇᴅ...\n\nError - {e}")
    else:
        index_temp.IS_INDEXINGS[user_id] = False
        time_taken = get_time(time.time() - start_time)
        await msg.reply("<b>ɪɴᴅᴇx ᴄᴏᴍᴘʟᴇᴛᴇᴅ ✅</b>")
        await msg.edit(f'<b>ɪɴᴅᴇx ᴄᴏᴍᴘʟᴇᴛᴇᴅ ✅\n\nᴛɪᴍᴇ ᴛᴀᴋᴇɴ - <code>{time_taken}</code>\n\nᴛᴏᴛᴀʟ ᴍᴇssᴀɢᴇs - <code>{total}</code>\nꜰᴇᴛᴄʜᴇᴅ ᴍᴇssᴀɢᴇs - <code>{fetched}</code>\nᴛᴏᴛᴀʟ sᴀᴠᴇᴅ ꜰɪʟᴇs - <code>{saved}</code>\nᴅᴜᴘʟɪᴄᴀᴛᴇ ꜰɪʟᴇs sᴋɪᴘᴘᴇᴅ - <code>{duplicate}</code>\nᴅᴇʟᴇᴛᴇᴅ ᴍᴇssᴀɢᴇs sᴋɪᴘᴘᴇᴅ - <code>{deleted}</code>\nᴜɴsᴜᴘᴘᴏʀᴛᴇᴅ ꜰɪʟᴇs sᴋɪᴘᴘᴇᴅ - <code>{unsupported}</code></b>')


async def iter_messages(bot, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator["types.Message", None]]:
    current = offset
    while True:
        new_diff = min(200, limit - current)
        if new_diff <= 0:
            return
        messages = await bot.get_messages(chat_id, list(range(current, current+new_diff+1)))
        for message in messages:
            yield message
            current += 1
