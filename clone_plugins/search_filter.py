import random
import asyncio
import re
import ast
import math
import time
from datetime import datetime, timedelta
from Script import script
from info import ADMINS, UPDATES_CHANNEL, FILES_CHANNEL, DELETE_TIME, LOG_CHANNEL, PICS, MAX_BTN, SUPPORT_GROUP, MOVIE_GROUP_LINK, UPDATES_CHANNEL_LINK, ON_WATCH, ON_DWNLD, F2LINK_C, CLONE_REQ_CHANNEL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ChatPermissions, InputMediaPhoto
from pyrogram import Client, filters, enums
from database.db import db
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid, ChatAdminRequired, MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from utils import get_size, temp, get_poster, get_time, is_clone_bot_force_subscribed, get_clone_bot_shortlink, encode, get_hash, imdb
from psutil import virtual_memory, disk_usage, cpu_percent
from clone_database.users_db import get_clone_bot_users_count
from clone_database.premium import is_premium_user
from clone_database.files_db import get_clone_bot_files_count, get_clone_bot_search_results, get_clone_bot_file_details
from database.files_db import total_files_count, get_file_details, get_search_results
from plugins.database import ub

from fuzzywuzzy import process
SEARCH = {}
MOVIE_LIST = {}
IMDB_TEMPLATE = {}

@Client.on_callback_query(filters.regex(r'^get_plan'))
async def get_plan_callback(client, query: CallbackQuery):
    me = await client.get_me()
    settings = await db.get_bot_settings(me.id)
    premium_text = settings.get('premium_text', "")
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ ⚠️", callback_data="close_plan")]
        ]
    )
    await query.message.reply_text(premium_text, reply_markup=reply_markup)

    
@Client.on_callback_query(filters.regex(r"^strm"))
async def stream_downloader(bot, query):
    me = await bot.get_me()
    settings = await db.get_bot_settings(me.id)
    file_unique_id = query.data.split('#', 1)[1]
    file = await get_file_details(file_unique_id)
    if not file:
        return await query.message.reply('<b>Files not found 😢</b>')
    sent_msg = await temp.BOT.send_cached_media(chat_id=FILES_CHANNEL, file_id=file['file_id'])
    msg = await bot.get_messages(FILES_CHANNEL, sent_msg.id)
    media = getattr(msg, msg.media.value)
    file_id = media.file_id
    msgk = await bot.send_cached_media(
        chat_id=F2LINK_C,
        file_id=file_id,
        caption="Your Caption Here"
    )
    online = f"https://{ON_WATCH}/watch/{msg.id}?hash={get_hash(msgk)}"
    download = f"https://{ON_DWNLD}/{msg.id}?hash={get_hash(msgk)}"
    await query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🖥️ Watch Online", url=online),
                    InlineKeyboardButton("📥 Fast Download", url=download)
                ]
            ]
        )
    )




@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    userid = message.from_user.id if message.from_user else 0
    search = message.text
    if not userid:
        await message.reply(f"<b>⚠️ ʏᴏᴜ'ʀ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ! ɪ'ᴍ ɴᴏᴛ ᴡᴏʀᴋɪɴɢ ꜰᴏʀ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴs ‼️</b>")
        return
    m = await message.reply(f"<b><code>{search}</code> Sᴇᴀʀᴄʜɪɴɢ...🔍</b>")
    await auto_filter(client, message, m)

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_filter(client, message):
    search = message.text
    m = await message.reply(f"<b><code>{search}</code> Sᴇᴀʀᴄʜɪɴɢ...🔍</b>")
    me = await client.get_me()
    settings = await db.get_bot_settings(me.id)
    if settings.get('pm_search'):
        await auto_filter(client, message, m)
    else:
        files, offset, total_results = await get_search_results(search, filter=True)
        if settings['group_link'] != "":
            user = message.from_user.first_name
            btn = [[
                InlineKeyboardButton("✧ ᴄʟɪᴄᴋ ʜᴇʀᴇ ✧", url=settings['group_link'])
            ]]
            await m.edit(f"<b>ʜᴇʏ {message.from_user.mention} 😍 ,\n\nʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ᴍᴏᴠɪᴇs ꜰʀᴏᴍ ʜᴇʀᴇ. ʀᴇǫᴜᴇsᴛ ɪᴛ ɪɴ ᴏᴜʀ ᴍᴏᴠɪᴇ ɢʀᴏᴜᴘ ᴏʀ ᴄʟɪᴄᴋ ʜᴇʀᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ 👇</b>", reply_markup=InlineKeyboardMarkup(btn))
        else:
            user = message.from_user.first_name
            default_url = "https://t.me/+v6h3boTBQXZlYWU1"  # Your default URL
            btn = [[
                InlineKeyboardButton("✧ ᴄʟɪᴄᴋ ʜᴇʀᴇ ✧", url=default_url)
            ]]
            await m.edit(f"<b>ʜᴇʏ {message.from_user.mention} 😍 ,\n\nʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ᴍᴏᴠɪᴇs ꜰʀᴏᴍ ʜᴇʀᴇ. ʀᴇǫᴜᴇsᴛ ɪᴛ ɪɴ ᴏᴜʀ ᴍᴏᴠɪᴇ ɢʀᴏᴜᴘ ᴏʀ ᴄʟɪᴄᴋ ʜᴇʀᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ 👇</b>", reply_markup=InlineKeyboardMarkup(btn))
            
        
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("⚠️ ᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀ ʀᴇsᴜʟᴛ ⁉️", show_alert=True)

    try:
        offset = int(offset)
    except:
        offset = 0

    search = SEARCH.get(key)
    if not search:
        await query.answer("🚸 ʏᴏᴜ ᴄʟɪᴄᴋɪɴɢ ᴏɴ ᴍʏ ᴏʟᴅ ᴍᴇssᴀɢᴇ, ᴘʟᴇᴀsᴇ ʀᴇǫᴜᴇsᴛ ᴀɢᴀɪɴ ♻️", show_alert=True)
        return

    message = query.message.reply_to_message
    me = await bot.get_me()
    cap = IMDB_TEMPLATE.get(key)
    settings = await db.get_bot_settings(me.id)
    del_msg = f"\n\n⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ {get_time(settings['auto_delete_time']).lower()} ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs 🗑" if settings['auto_delete'] else ""
    max_results = settings['max_results']
    files, n_offset, total = await get_search_results(search, max_results=max_results, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return await query.answer("ɴᴏ ꜰɪʟᴇs ꜰᴏᴜɴᴅ 😐", show_alert=True)

    files_link = ""
    if settings['clone_buttons']:
        btn = [[
            InlineKeyboardButton(text=f"{get_size(file['file_size'])} {file['file_name']}", callback_data=f"file#{req}#{file['_id']}")
        ]
               for file in files
              ]
    else:
        btn = []
        for file_num, file in enumerate(files, start=offset+1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://telegram.me/{me.username}?start=file_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""

    btn.insert(0,
        [InlineKeyboardButton('📜 sᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ 📜', callback_data=f"bot_languages#{req}#{key}#{offset}")]
    )

  #  if settings['tutorial'] != "":
   #     btn.insert(0,
    #        [InlineKeyboardButton('⁉️ ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ ⁉️', url=settings['tutorial'])]
    #    )

    if 0 < offset <= max_results:
        b_offset = 0
    elif offset == 0:
        b_offset = None
    else:
        b_offset = offset - max_results

    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("≼ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{b_offset}"),
             InlineKeyboardButton(f"ᴘᴀɢᴇs {math.ceil(int(offset) / max_results) + 1} / {math.ceil(total / max_results)}", callback_data="pages")]
        )
    elif b_offset is None:
        btn.append(
            [InlineKeyboardButton(f"ᴘᴀɢᴇs {math.ceil(int(offset) / max_results) + 1} / {math.ceil(total / max_results)}", callback_data="pages"),
             InlineKeyboardButton("ɴᴇxᴛ ≽", callback_data=f"next_{req}_{key}_{n_offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton("≼ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{b_offset}"),
             InlineKeyboardButton(f"{math.ceil(int(offset) / max_results) + 1} / {math.ceil(total / max_results)}", callback_data="pages"),
             InlineKeyboardButton("ɴᴇxᴛ ≽", callback_data=f"next_{req}_{key}_{n_offset}")]
        )
    btn.append(
        [InlineKeyboardButton("‼️ ᴄʟᴏsᴇ ‼️", callback_data=f"close#{req}")]
    )
    await query.message.edit(cap+files_link+del_msg, reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"^bot_languages"))
async def languages(bot, query):
    ident, req, key, offset = query.data.split("#")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("⚠️ ᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀ ʀᴇsᴜʟᴛ ⁉️", show_alert=True)

    langs = ['english', 'tamil', 'hindi', 'malayalam', 'kannada', 'telugu']
    btn = [[
        InlineKeyboardButton(text=lang.title(), callback_data=f"bot_lang_search#{req}#{key}#{lang}#{offset}")
    ]
        for lang in langs
    ]
    btn.append(
        [InlineKeyboardButton("≼ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{offset}")]
    )
    await query.message.edit('<b>ɪɴ ᴡʜɪᴄʜ ʟᴀɴɢᴜᴀɢᴇ ʏᴏᴜ ᴡᴀɴᴛ, ᴄʜᴏᴏsᴇ ʜᴇʀᴇ 👇</b>', reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"^bot_lang_search"))
async def lang_search(bot, query):
    ident, req, key, lang, offset = query.data.split("#")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("⚠️ ᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀ ʀᴇsᴜʟᴛ ⁉️", show_alert=True)

    search = SEARCH.get(key)
    cap = IMDB_TEMPLATE.get(key)
    if not search or not cap:
        await query.answer("🚸 ʏᴏᴜ ᴄʟɪᴄᴋɪɴɢ ᴏɴ ᴍʏ ᴏʟᴅ ᴍᴇssᴀɢᴇ, ᴘʟᴇᴀsᴇ ʀᴇǫᴜᴇsᴛ ᴀɢᴀɪɴ ♻️", show_alert=True)
        return
    files, l_offset, total_results = await get_search_results(search, filter=True, language=lang)
    if not files:
        await query.answer('sᴏʀʀʏ, ᴛʜɪs ʟᴀɴɢᴜᴀɢᴇ ꜰɪʟᴇs ɴᴏᴛ ꜰᴏᴜɴᴅ 🚫', show_alert=True)
        return
    me=await bot.get_me()
    settings = await db.get_bot_settings(me.id)
    del_msg = f"\n\n⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ {get_time(settings['auto_delete_time']).lower()} ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs 🗑" if settings['auto_delete'] else ""
    files_link = ""
    if settings['clone_buttons']:
        btn = [[
            InlineKeyboardButton(text=f"{get_size(file['file_size'])} {file['file_name']}", callback_data=f"""file#{req}#{file['_id']}""")
        ]
            for file in files
        ]
    else:
        btn = []
        for file_num, file in enumerate(files, start=1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://telegram.me/{me.username}?start=file_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""
    #if settings['tutorial'] != "":
    #    btn.insert(0,
    #        [InlineKeyboardButton('⁉️ ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ ⁉️', url=settings['tutorial'])]
    #    )
    if l_offset != "":
        btn.append(
            [InlineKeyboardButton(text=f"ᴘᴀɢᴇs 1/{math.ceil(int(total_results) / MAX_BTN)}", callback_data="pages"),
             InlineKeyboardButton(text="ɴᴇxᴛ ≽", callback_data=f"bot_lang_next#{req}#{key}#{lang}#{l_offset}#{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🔘 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs ᴀᴠᴀɪʟᴀʙʟᴇ 🔘", callback_data="pages")]
        )
    btn.append(
        [InlineKeyboardButton("≼ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{offset}")]
    )
    await query.message.edit(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)

@Client.on_callback_query(filters.regex(r"^bot_lang_next"))
async def lang_next_page(bot, query):
    ident, req, key, lang, l_offset, offset = query.data.split("#")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("⚠️ ᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀ ʀᴇsᴜʟᴛ ⁉️", show_alert=True)

    try:
        l_offset = int(l_offset)
    except:
        l_offset = 0

    search = SEARCH.get(key)
    cap = IMDB_TEMPLATE.get(key)
    if not search or not cap:
        await query.answer("🚸 ʏᴏᴜ ᴄʟɪᴄᴋɪɴɢ ᴏɴ ᴍʏ ᴏʟᴅ ᴍᴇssᴀɢᴇ, ᴘʟᴇᴀsᴇ ʀᴇǫᴜᴇsᴛ ᴀɢᴀɪɴ ♻️", show_alert=True)
        return

    me=await bot.get_me()
    settings = await db.get_bot_settings(me.id)
    files, n_offset, total = await get_search_results(search, offset=l_offset, filter=True, language=lang)
    if not files:
        return await query.answer("ɴᴏ ꜰɪʟᴇs ꜰᴏᴜɴᴅ 😐", show_alert=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    files_link = ""
    if settings['clone_buttons']:
        btn = [[
            InlineKeyboardButton(text=f"{get_size(file['file_size'])} {file['file_name']}", callback_data=f"""file#{req}#{file['_id']}""")
        ]
            for file in files
        ]
    else:
        btn = []
        for file_num, file in enumerate(files, start=l_offset+1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://telegram.me/{me.username}?start=file_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""

    if 0 < l_offset <= MAX_BTN:
        b_offset = 0
    elif l_offset == 0:
        b_offset = None
    else:
        b_offset = l_offset - MAX_BTN

    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("≼ ʙᴀᴄᴋ", callback_data=f"bot_lang_next#{req}#{key}#{lang}#{b_offset}#{offset}"),
             InlineKeyboardButton(f"ᴘᴀɢᴇs {math.ceil(int(l_offset) / MAX_BTN) + 1} / {math.ceil(total / MAX_BTN)}", callback_data="pages")]
        )
    elif b_offset is None:
        btn.append(
            [InlineKeyboardButton(f"ᴘᴀɢᴇs {math.ceil(int(l_offset) / MAX_BTN) + 1} / {math.ceil(total / MAX_BTN)}", callback_data="pages"),
             InlineKeyboardButton("ɴᴇxᴛ ≽", callback_data=f"bot_lang_next#{req}#{key}#{lang}#{n_offset}#{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton("≼ ʙᴀᴄᴋ", callback_data=f"bot_lang_next#{req}#{key}#{lang}#{b_offset}#{offset}"),
             InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1} / {math.ceil(total / MAX_BTN)}", callback_data="pages"),
             InlineKeyboardButton("ɴᴇxᴛ ≽", callback_data=f"bot_lang_next#{req}#{key}#{lang}#{n_offset}#{offset}")]
        )
    btn.append(
        [InlineKeyboardButton("≼ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{offset}")]
    )
    await query.message.edit_text(cap + files_link, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)


@Client.on_callback_query(filters.regex(r"^spolling"))
async def spolling_checking(bot, query):
    _, key, user, movie_num = query.data.split('#')
    if int(user) not in [query.from_user.id, 0]:
        return await query.answer("⚠️ ᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀ ʀᴇsᴜʟᴛ ⁉️", show_alert=True)

    movie_list = MOVIE_LIST.get(key)
    if not movie_list:
        await query.answer("🚸 ʏᴏᴜ ᴄʟɪᴄᴋɪɴɢ ᴏɴ ᴍʏ ᴏʟᴅ ᴍᴇssᴀɢᴇ, ᴘʟᴇᴀsᴇ ʀᴇǫᴜᴇsᴛ ᴀɢᴀɪɴ ♻️", show_alert=True)
        return
    search = movie_list[int(movie_num)]
    m = await query.message.edit_text(f"<b><code>{search}</code> ᴄʜᴇᴄᴋɪɴɢ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ 📥...</b>")
    me = await bot.get_me()
    settings = await db.get_bot_settings(me.id)
    files, offset, total_results = await get_search_results(search, max_results=settings['max_results'], filter=True)
    if files:
        spoll = (search, files, offset, total_results)
        await m.delete()
        await auto_filter(bot, query, spoll)
    else:
        k = await query.message.edit(f"<b>🪭 ʜᴇʟʟᴏ {query.from_user.mention},\n\nɪ ᴅᴏɴ'ᴛ ꜰɪɴᴅ <code>{search}</code> ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ᴏʀ ɴᴏᴛ ʀᴇʟᴇᴀsᴇᴅ ʏᴇᴛ 🌚</b>")
        await asyncio.sleep(60)
        await k.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    me = await client.get_me()
    bot = await db.get_bot(me.id)
    admin = bot['_id']
    has_premium = await ub.has_premium_access(admin)
    settings = await db.get_bot_settings(me.id)

    if query.data.startswith("close"):
        ident, userid = query.data.split("#")
        if int(userid) not in [query.from_user.id, 0]:
            return await query.answer("⚠️ ᴛʜɪs ɪs ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ", show_alert=True)

        await query.answer("🗑")
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass


    elif query.data.startswith("file"):
        ident, req, file_unique_id = query.data.split("#")
        if int(req) not in [query.from_user.id, 0]:
            return await query.answer("⚠️ ᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀ ʀᴇsᴜʟᴛ ⁉️", show_alert=True)
        await query.answer(url=f"https://telegram.me/{me.username}?start=file_{file_unique_id}")


    elif query.data == 'help':
        text = """<b>Its easy to use me just add me to your group and send any movie name !

<u>Available Commands:</u>

/start - sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ.
/stats - ɢᴇᴛ ʙᴏᴛ sᴛᴀᴛᴜs.
/users - ɢᴇᴛ ᴀʟʟ ʙᴏᴛ ᴜsᴇʀs.
/broadcast - ʙʀᴏᴀᴅᴄᴀsᴛ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙᴏᴛ ᴜsᴇʀs. (ᴏᴡɴᴇʀ ᴏɴʟʏ !)</b>"""
        btn = [[
            InlineKeyboardButton('🗼 ʜᴏᴍᴇ', callback_data='start')
        ]]
        await query.message.edit(text, reply_markup=InlineKeyboardMarkup(btn))

    elif query.data == 'about':
        text = """<b><u>✨ About Me</u>
        
ᴍʏ ɴᴀᴍᴇ: {}
ᴍʏ ᴏᴡɴᴇʀ - {}
ᴄʟᴏɴᴇᴅ ꜰʀᴏᴍ - <a href=https://t.me/{}>{}</a>
ꜱᴜᴘᴘᴏʀᴛ - <a href=https://t.me/CloneV2Support>ʜᴇʀᴇ</a></b>"""
        btn = [[
            InlineKeyboardButton('🗼 ʜᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('ᴄʟᴏsᴇ 🗑️', callback_data=f"close#{query.from_user.id}")
        ]]
        await query.message.edit(text.format(me.mention, bot['owner'], temp.BOT_USERNAME, temp.BOT_NAME), disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(btn))

    elif query.data == 'status':
        await query.answer('♻️ ᴄᴀʟᴄᴜʟᴀᴛɪɴɢ...')
        text = """<b><u>Current Bot Stats:</u>
        
🗂 ꜰɪʟᴇs - <code>{}</code>
👤 ᴜsᴇʀs - <code>{}</code>
💤 ᴜᴘᴛɪᴍᴇ - <code>{}</code>
⏰ ᴛɪᴍᴇꜱᴛᴀᴍᴘ : <code>{}</code></b>"""
        btn = [[
            InlineKeyboardButton('🗼 ʜᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('ᴄʟᴏsᴇ 🗑️', callback_data='status')
        ]]
        uptime = get_time(time.time() - temp.CLONE_BOTS_START_TIME.get(me.id))
        files = await total_files_count()
        users = await get_clone_bot_users_count(me.id)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await query.message.edit(text.format(files, users, uptime, timestamp), reply_markup=InlineKeyboardMarkup(btn))

    elif query.data == 'start':
        btn = [[
            InlineKeyboardButton('⇄ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⇆', url=f'http://t.me/{me.username}?startgroup=start')
        ],[
            InlineKeyboardButton('⚠️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ 📚', callback_data='about')
        ]]
        if 'button_text' in settings and settings['button_text'] and 'button_url' in settings and settings['button_url']:
            btn.append([
                InlineKeyboardButton(settings['button_text'], url=settings['button_url'])
            ])
        if has_premium and settings.get('sec_button_text') and settings.get('sec_button_url'):
            btn.append([
                InlineKeyboardButton(settings['sec_button_text'], url=settings['sec_button_url'])
            ])
        await query.message.edit(text=settings['start_text'].format(mention=query.from_user.mention), disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(btn))

    elif query.data == "pages":
        await query.answer("‼️")

    elif query.data == "instructions":
        await query.answer(script.INSTRUCTIONS_TXT, show_alert=True)

    elif query.data == "tips":
        await query.answer(script.INSTRUCTIONS_TXT, show_alert=True)

async def ai_spell_check(wrong_name):
    async def search_movie(wrong_name):
        search_results = imdb.search_movie(wrong_name)
        movie_list = [movie['title'] for movie in search_results]
        return movie_list
    movie_list = await search_movie(wrong_name)
    if not movie_list:
        return
    for _ in range(5):
        closest_match = process.extractOne(wrong_name, movie_list)
        if not closest_match or closest_match[1] <= 80:
            return 
        movie = closest_match[0]
        files, offset, total_results = await get_search_results(movie)
        if files:
            return movie
        movie_list.remove(movie)
    return
        
async def auto_filter(client, msg, s, spoll=False):
    me = await client.get_me()
    settings = await db.get_bot_settings(me.id)
    if not spoll:
        message = msg
        if message.text.startswith("/"):
            return

        if re.findall("[\u0D80-\u0DFF]", message.text):
            await message.reply("<b>මට සිංහල අකුරු කියවන්න බෑනේ. 💔</b>")

        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return

        query = message.text
        files, offset, total_results = await get_search_results(query, max_results=settings['max_results'], filter=True)
        if not files:
            ai_sts = await s.edit('<b>𝘈𝘤𝘵𝘪𝘷𝘢𝘵𝘦 𝘢𝘥𝘷𝘢𝘯𝘤𝘦 𝘴𝘱𝘦𝘭𝘭 𝘤𝘩𝘦𝘤𝘬 𝘮𝘰𝘥𝘦 ✅</b>')
            is_misspelled = await ai_spell_check(query)
            if is_misspelled:
                k = await ai_sts.edit(f'<b>𝘈𝘪 𝘚𝘶𝘨𝘨𝘦𝘴𝘵𝘦𝘥 <code>{is_misspelled}</code> 𝘚𝘰 𝘐𝘮 𝘚𝘦𝘢𝘳𝘤𝘩𝘪𝘯𝘨 𝘧𝘰𝘳 <code>{is_misspelled}</code> 👀</b>')
                msg.text = is_misspelled
                return await auto_filter(client, msg, k)
            return await spelling_check(message, s, settings)

    else:
        message = msg.message.reply_to_message
        query, files, offset, total_results = spoll

    key = f"{message.chat.id}-{message.id}"
    SEARCH[key] = query
    req = message.from_user.id if message.from_user else 0
    
    files_link = ""
    if settings['clone_buttons']:
        btn = [[
            InlineKeyboardButton(text=f"{get_size(file['file_size'])} {file['file_name']}", callback_data=f"file#{req}#{file['_id']}")
        ]
               for file in files
              ]
    else:
        btn = []
        for file_num, file in enumerate(files, start=1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://telegram.me/{me.username}?start=file_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""

    if offset != "":
        btn.insert(0,
            [InlineKeyboardButton('📜 sᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ 📜', callback_data=f"bot_languages#{req}#{key}#{0}")]
        )
        
        btn.append(
            [InlineKeyboardButton(text=f"ᴘᴀɢᴇs 1 / {math.ceil(int(total_results) / settings['max_results'])}", callback_data="pages"),
             InlineKeyboardButton(text="ɴᴇxᴛ ≽", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🔘 ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇs ᴀᴠᴀɪʟᴀʙʟᴇ 🔘", callback_data="pages")]
        )
    btn.append(
        [InlineKeyboardButton("‼️ ᴄʟᴏsᴇ ‼️", callback_data=f"close#{req}")]
    )

    try:
        imdb = await get_poster(query, file=(files[0])['file_name'])
        cap = settings['imdb_template'].format(
            mention=message.from_user.mention,
            group=message.chat.title,
            search=query,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    except:
        cap = script.FILE_TEMPLATE.format(query, message.from_user.mention, message.chat.title)

    caption = cap
    del_msg = f"\n\n⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ {get_time(settings['auto_delete_time']).lower()} ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs 🗑" if settings['auto_delete'] else ""
    
    IMDB_TEMPLATE[key] = caption
    
    if settings['imdb_poster']:
        try:
            await s.delete()
            m = await message.reply_photo(photo=imdb.get('poster'), caption=caption + files_link+del_msg, has_spoiler=True, reply_markup=InlineKeyboardMarkup(btn))
            if settings['auto_delete']:
                await asyncio.sleep(settings['auto_delete_time'])
                await m.delete()
                try:
                    await message.delete()
                except:
                    pass
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            await s.delete()
            m = await message.reply_photo(photo=poster, caption=caption + files_link+del_msg, has_spoiler=True, reply_markup=InlineKeyboardMarkup(btn))
            if settings['auto_delete']:
                await asyncio.sleep(settings['auto_delete_time'])
                await m.delete()
                try:
                    await message.delete()
                except:
                    pass
        except Exception as e:
            m = await s.edit(caption + files_link+del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
            if settings['auto_delete']:
                await asyncio.sleep(settings['auto_delete_time'])
                await m.delete()
                try:
                    await message.delete()
                except:
                    pass
    else:
        m = await s.edit(caption + files_link+del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        if settings['auto_delete']:
            await asyncio.sleep(settings['auto_delete_time'])
            await m.delete()
            try:
                await message.delete()
            except:
                pass


async def spelling_check(message, s, settings):
    if settings.get('spell_check'):
        search = message.text
        google_search = search.replace(" ", "+")
        btn = [[
            InlineKeyboardButton("🔍 ɢᴏᴏɢʟᴇ sᴇᴀʀᴄʜ 🔍", url=f"https://www.google.com/search?q={google_search}")
        ]]
        try:
            await s.delete()
            movies = await get_poster(search, bulk=True, results=20)
        except Exception:
            notification = await message.reply(
                script.NOT_FILE_TXT.format(message.from_user.mention, search),
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await asyncio.sleep(60)
            await notification.delete()
            try:
                await message.delete()
            except Exception:
                pass
            return
        if not movies:
            notification = await message.reply(
                script.NOT_FILE_TXT.format(message.from_user.mention, search),
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await asyncio.sleep(60)
            await notification.delete()
            try:
                await message.delete()
            except Exception:
                pass
            return
        movie_list = list({movie.get('title') for movie in movies})  # removing duplicates
        key = f"{message.chat.id}-{message.id}"
        MOVIE_LIST[key] = movie_list
        user = message.from_user.id if message.from_user else 0

        buttons = [
            [InlineKeyboardButton(text=movie_name, callback_data=f"spolling#{key}#{user}#{movie_num}")]
            for movie_num, movie_name in enumerate(movie_list)
        ]
        buttons.append([
            InlineKeyboardButton("‼️ ᴄʟᴏsᴇ ‼️", callback_data=f"close#{user}")
        ])
        notification = await message.reply(
            f"<b>🎎 ʜᴇʏ {message.from_user.mention},\n\n"
            f"ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ {search} ʏᴏᴜ ʀᴇǫᴜᴇsᴛᴇᴅ,\n"
            f"sᴇʟᴇᴄᴛ ɪꜰ ʏᴏᴜ ᴍᴇᴀɴᴛ ᴏɴᴇ ᴏꜰ ᴛʜᴇsᴇ??👇</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await asyncio.sleep(300)
        await notification.delete()
        try:
            await message.delete()
        except Exception:
            pass
