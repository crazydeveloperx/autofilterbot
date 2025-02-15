import asyncio
import re
import time
import string
import ast
import math
import pytz
from datetime import datetime, timedelta
from Script import script
from pyrogram.errors import FloodWait, UserIsBlocked, MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty, MessageNotModified, PeerIdInvalid, ChatAdminRequired
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ChatPermissions, InputMediaPhoto, BotCommand
from pyrogram import Client, filters, enums
from utils import get_size, decode, encode, update_settings, get_settings, is_subscribed, get_poster, temp, is_joined, get_time, get_shortlink, au_restart_all_bots
from database.db import db
from plugins.database import ub
from clone_database.users_db import *
from clone_database.premium import *
from info import ADMINS, API_ID, API_HASH, LOG_CHANNEL

@Client.on_callback_query(filters.regex(r"^add_premium#"))
async def add_premium(client: Client, query):
    try:
        _, bot_id, user_id, duration = query.data.split("#")
        user_id = int(user_id)
        days = int(duration.replace("days", ""))
        expiry_time = datetime.now(pytz.UTC) + timedelta(days=days)
        
        user_data = {
            "id": user_id,
            "expiry_time": expiry_time,
            "bot_id": int(bot_id)
        }
        await update_user(user_data)
        clone_bot = temp.CLONE_BOTS.get(query.from_user.id)
        await clone_bot.send_message(chat_id=user_id, text=f"<b><u>Premium added✅</u> to your account for {days}. Enjoy! 😀</b>")
        await query.message.edit_text(
            f"<b>Pʀᴇᴍɪᴜᴍ Aᴄᴄᴇꜱꜱ Aᴅᴅᴇᴅ Tᴏ Uꜱᴇʀ Iᴅ {user_id} Fᴏʀ {days} Dᴀʏꜱ.</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Bᴀᴄᴋ", callback_data=f"bot_prime_setgs#{bot_id}")]
            ])
        )
    except ValueError:
        await query.message.edit_text("Invalid data received in callback query.")
    except Exception as e:
        await query.message.edit_text(f"An error occurred: {str(e)}")
        
@Client.on_callback_query(filters.regex(r'^add_bot'))
async def add_bot(bot, query):
    await query.message.delete()
    b = await query.message.reply("<b>1) sᴇɴᴅ <code>/newbot</code> ᴛᴏ @BotFather\n2) ɢɪᴠᴇ ᴀ ɴᴀᴍᴇ ꜰᴏʀ ʏᴏᴜʀ ʙᴏᴛ.\n3) ɢɪᴠᴇ ᴀ ᴜɴɪǫᴜᴇ ᴜsᴇʀɴᴀᴍᴇ.\n4) ᴛʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏᴋᴇɴ.\n5) ꜰᴏʀᴡᴀʀᴅ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ ᴛᴏ ᴍᴇ.\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss.</b>")
    
    try:
        msg = await bot.listen(query.message.chat.id)
        if msg.text == '/cancel':
            await b.delete()
            return await query.message.reply('<b>ᴄᴀɴᴄᴇʟᴇᴅ ᴛʜɪs ᴘʀᴏᴄᴇss 🚫</b>')
        if msg.forward_from and msg.forward_from.id == 93372553:
            try:
                bot_token = re.findall(r"\b(\d+:[A-Za-z0-9_-]+)\b", msg.text)[0]
            except:
                await b.delete()
                return await query.message.reply('<b>sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ 😕</b>')
        else:
            await b.delete()
            return await query.message.reply('<b>ɴᴏᴛ ꜰᴏʀᴡᴀʀᴅᴇᴅ ꜰʀᴏᴍ @BotFather 😑</b>')
        await b.delete()
        # Assuming db.is_bot_found_using_token and other functions are defined elsewhere
        token_found = await db.is_bot_found_using_token(bot_token)
        if token_found:
            return await query.message.edit("<b>⚠️ ᴏᴏᴘs! ᴛʜɪs ʙᴏᴛ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ...</b>")
        c = await query.message.reply('<b>🧑‍💻 ᴄʜᴇᴄᴋɪɴɢ ɪɴꜰᴏ...</b>')
        clone_bot = Client(
            name=bot_token,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=bot_token,
            plugins={"root": "clone_plugins"}
        )
        try:
            await clone_bot.start()
        except Exception as e:
            await c.edit(f'Error - <code>{e}</code>')
            return
        me = await clone_bot.get_me()
        temp.CLONE_BOTS_START_TIME[me.id] = time.time()
        temp.CLONE_BOTS[query.from_user.id] = clone_bot
        await clone_bot.set_bot_commands(
            [BotCommand("start", "Start The Bot!"),
             BotCommand("stats", "Get Bot Status."),
             BotCommand("myplan", "Check Premium Status."),
             BotCommand("broadcast", "Broadcast Message to bot users.")]
        )
        if query.from_user.username:
            owner = f"<a href='https://t.me/{query.from_user.username}'>{query.from_user.first_name}</a>"
        else:
            owner = f"<a href='tg://user?id={query.from_user.id}'>{query.from_user.first_name}</a>"
        await db.add_bot(query.from_user.id, owner, me.id, bot_token, me.username)
        tz = pytz.timezone('Asia/Colombo')
        await db.update_bot_last_used(me.id, datetime.now(tz))
        await bot.send_message(LOG_CHANNEL, f'New bot created by {me.username}')
        btn = [[
            InlineKeyboardButton("🖋️ ᴄᴜsᴛᴏᴍɪᴢᴇ ʙᴏᴛ", callback_data='clone_bot_settings')
        ]]
        await c.edit(f'<b>ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴ ʏᴏᴜʀ @{me.username} ʙᴏᴛ ɪs sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʀᴇᴀᴛᴇᴅ. ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ 🙂\n\nʏᴏᴜ ᴄᴀɴ ᴄᴜsᴛᴏᴍɪᴢᴇ ʏᴏᴜʀ ʙᴏᴛ ᴜsɪɴɢ ʙᴇʟʟᴏᴡ ʙᴜᴛᴛᴏɴ</b>', reply_markup=InlineKeyboardMarkup(btn))
        await asyncio.sleep(0.2)
        await query.message.reply("<b>ᴀɴᴅ ᴅᴏɴ'ᴛ ꜰᴏʀɢᴇᴛ ᴛᴏ ᴀᴅᴅ ʟᴏɢ ᴄʜᴀɴɴᴇʟ 😐...\n\nᴡʜᴀᴛ ɪs ʟᴏɢ ᴄʜᴀɴɴᴇʟ?\n\nɪꜰ ᴀɴʏ ᴜsᴇʀ sᴛᴀʀᴛs ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ, ᴛʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ᴛʜᴇ ᴅᴀᴛᴀ ᴏꜰ ᴛʜᴀᴛ ᴜsᴇʀ ɪɴ ᴛʜᴇ ʟᴏɢ ᴄʜᴀɴɴᴇʟ. sᴇɴᴅ /clone ᴄᴏᴍᴍᴀɴᴅ ᴀɴᴅ ᴀᴅᴅ.</b>")
    except Exception as e:
        print(e)

@Client.on_callback_query(filters.regex(r"^restart_all_bots$"))
async def handle_ac_restart_all_bots(client: Client, query: CallbackQuery):
    if query.from_user.id not in ADMINS:
        await query.answer("You do not have permission to use this command.", show_alert=True)
        return
    await au_restart_all_bots(query)

@Client.on_callback_query()
async def query_handler(client: Client, query: CallbackQuery):
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

    elif query.data == "confirm_bot_delete":
        bot = await db.get_bot_from_user(query.from_user.id)
        await db.delete_bot(query.from_user.id)
        await query.message.edit_text(f"<b>sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ʏᴏᴜʀ @{bot['username']} ᴄʟᴏɴᴇ ʙᴏᴛ.\n\nɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴏᴛʜᴇʀ ɴᴇᴡ ᴄʟᴏɴᴇ ʙᴏᴛ ᴛʜᴇɴ ᴄʀᴇᴀᴛᴇ ᴜsɪɴɢ /clone ᴄᴏᴍᴍᴀɴᴅ</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data='start')]]))
        clone_bot = temp.CLONE_BOTS.get(query.from_user.id)
        try:
            await clone_bot.stop()
        except:
            pass


    elif query.data.startswith("bot_force_channel_setgs"):
        _, bot_id = query.data.split("#")
        settings = await db.get_bot_settings(int(bot_id))
        if not settings['is_active']:
            await query.answer("🚫 ʏᴏᴜʀ ʙᴏᴛ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ, ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜɪs...", show_alert=True)
            return
        if 'req_fsub' not in settings:
            settings['req_fsub'] = False
        req_fsub = settings['req_fsub']
        btn = [[
            InlineKeyboardButton('sᴇᴛ ᴄʜᴀɴɴᴇʟ ', callback_data=f'bot_set_force_channel#{bot_id}'),
            InlineKeyboardButton('ᴅᴇʟᴇᴛᴇ ᴄʜᴀɴɴᴇʟ', callback_data=f'bot_force_channel_delete#{bot_id}')
        ],[
            InlineKeyboardButton('Oꜰꜰ RᴇQ Fꜱᴜʙ' if settings['req_fsub'] else 'Oɴ RᴇQ Fꜱᴜʙ', callback_data=f"bot_update_req_fsub#{bot_id}#{settings['req_fsub']}"),
            InlineKeyboardButton('ᴏꜰꜰ sᴜʙsᴄʀɪʙᴇ' if settings['force_subscribe'] else 'ᴏɴ sᴜʙsᴄʀɪʙᴇ', callback_data=f"bot_update_force_subscribe#{bot_id}#{settings['force_subscribe']}")
        ],[
            InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data=f'bot_settings#{bot_id}')
        ]]
        subscribe = 'ᴏɴ ✅' if settings['force_subscribe'] else 'ᴏꜰꜰ ❌'
        req_fsubs = 'ᴏɴ ✅' if settings['req_fsub'] else 'ᴏꜰꜰ ❌'
        if settings['force_channel'] == "":
            channel = "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟ..."
        else:
            clone_bot = temp.CLONE_BOTS.get(query.from_user.id)
            chat = await clone_bot.get_chat(settings['force_channel'])
            channel = f"Force Channel: {chat.title}"
        await query.message.edit(f"ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟ ɪɴ ɢɪᴠᴇ ꜰɪʟᴇs.\n\nsᴜʙsᴄʀɪʙᴇ - {subscribe}\nRᴇQᴜᴇꜱᴛ Fꜱᴜʙ - {req_fsubs}\n\n{channel}", reply_markup=InlineKeyboardMarkup(btn))
    elif query.data.startswith("bot_update_force_subscribe"):
        _, bot_id, status = query.data.split("#")
        settings = await db.get_bot_settings(int(bot_id))
        if not settings['is_active']:
            await query.answer("🚫 ʏᴏᴜʀ ʙᴏᴛ ɪs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ, ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜɪs...", show_alert=True)
            return
        if settings['force_channel'] == "":
            await query.answer("ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ.", show_alert=True)
            return
        if status == 'True':
            await db.update_bot_settings(int(bot_id), 'force_subscribe', False)
        else:
            await db.update_bot_settings(int(bot_id), 'force_subscribe', True)
        settings = await db.get_bot_settings(int(bot_id))
        btn = [[
            InlineKeyboardButton('sᴇᴛ ᴄʜᴀɴɴᴇʟ ', callback_data=f'bot_set_force_channel#{bot_id}'),
            InlineKeyboardButton('ᴅᴇʟᴇᴛᴇ ᴄʜᴀɴɴᴇʟ', callback_data=f'bot_force_channel_delete#{bot_id}')
        ],[
            InlineKeyboardButton('Oꜰꜰ RᴇQ Fꜱᴜʙ' if settings['req_fsub'] else 'Oɴ RᴇQ Fꜱᴜʙ', callback_data=f"bot_update_req_fsub#{bot_id}#{settings['req_fsub']}"),
            InlineKeyboardButton('ᴏꜰꜰ sᴜʙsᴄʀɪʙᴇ' if settings['force_subscribe'] else 'ᴏɴ sᴜʙsᴄʀɪʙᴇ', callback_data=f"bot_update_force_subscribe#{bot_id}#{settings['force_subscribe']}")
        ],[
            InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data=f'bot_settings#{bot_id}')
        ]]
        subscribe = 'ᴏɴ ✅' if settings['force_subscribe'] else 'ᴏꜰꜰ ❌'
        req_fsubs = 'ᴏɴ ✅' if settings['req_fsub'] else 'ᴏꜰꜰ ❌'
        if settings['force_channel'] == "":
            channel = "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ."
        else:
            clone_bot = temp.CLONE_BOTS.get(query.from_user.id)
            chat = await clone_bot.get_chat(settings['force_channel'])
            channel = f"ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ - {chat.title}"
        await query.message.edit(f"ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟ ɪɴ ɢɪᴠᴇ ꜰɪʟᴇs.\n\nsᴜʙsᴄʀɪʙᴇ - {subscribe}\nRᴇQᴜᴇꜱᴛ Fꜱᴜʙ - {req_fsubs}\n\n{channel}", reply_markup=InlineKeyboardMarkup(btn))
    elif query.data.startswith("bot_force_channel_delete"):
        _, bot_id = query.data.split("#")
        btn = [[
            InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data=f'bot_force_channel_setgs#{bot_id}')
        ]]
        settings = await db.get_bot_settings(int(bot_id))
        if settings['force_channel'] == "":
            await query.answer("ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟ...", show_alert=True)
            return
        await db.update_bot_settings(int(bot_id), 'force_subscribe', False)
        await db.update_bot_settings(int(bot_id), 'force_channel', "")
        await query.message.edit_text("sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ 🗑", reply_markup=InlineKeyboardMarkup(btn))
    elif query.data.startswith("bot_set_force_channel"):
        _, bot_id = query.data.split("#")
        bot = await db.get_bot(int(bot_id))
        btn = [[
            InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data=f'bot_force_channel_setgs#{bot_id}')
        ]]
        await query.message.edit_text(f"ꜰᴏʀᴡᴀʀᴅ ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴛᴏ ᴍᴇ.\nᴀɴᴅ ᴍᴀᴋᴇ sᴜʀᴇ @{bot['username']} ɪs ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ  ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ.\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss.")
        msg = await client.listen(query.from_user.id)
        if msg.text == '/cancel':
            await query.message.delete()
            await query.message.reply("ᴄᴀɴᴄᴇʟʟᴇᴅ ᴛʜɪs ᴘʀᴏᴄᴇss...", reply_markup=InlineKeyboardMarkup(btn))
            return
        if msg.forward_from_chat and msg.forward_from_chat.type == enums.ChatType.CHANNEL:
            chat_id = msg.forward_from_chat.id
        else:
            await query.message.delete()
            await query.message.reply('😒 ɴᴏᴛ ꜰᴏʀᴡᴀʀᴅ ꜰʀᴏᴍ ᴄʜᴀɴɴᴇʟ...', reply_markup=InlineKeyboardMarkup(btn))
            return
        clone_bot = temp.CLONE_BOTS.get(query.from_user.id)
        await query.message.delete()
        try:
            chat = await clone_bot.get_chat(chat_id)
            link = await clone_bot.create_chat_invite_link(chat.id)
        except Exception as e:
            await query.message.reply(f'‼️ sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ\n\n<code>{e}</code>', reply_markup=InlineKeyboardMarkup(btn))
            return
        await db.update_bot_settings(int(bot_id), 'force_channel', chat.id)
        await query.message.reply(f"💥 sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴀᴅᴅᴇᴅ ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ - {chat.title}", reply_markup=InlineKeyboardMarkup(btn))
    elif query.data.startswith("bot_log_channel_setgs"):
        _, bot_id = query.data.split("#")
        settings = await db.get_bot_settings(int(bot_id))
        if not settings['is_active']:
            await query.answer("ʏᴏᴜʀ ʙᴏᴛ ɪs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ, ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜɪs", show_alert=True)
            return
        btn = [[
            InlineKeyboardButton('sᴇᴛ ᴄʜᴀɴɴᴇʟ', callback_data=f'bot_set_log_channel#{bot_id}'),
            InlineKeyboardButton('ᴅᴇʟᴇᴛᴇ ᴄʜᴀɴɴᴇʟ', callback_data=f'bot_log_channel_delete#{bot_id}')
        ],[
            InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data=f'bot_settings#{bot_id}')
        ]]
        if settings['log_channel'] == "":
            channel = "**ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ʟᴏɢ ᴄʜᴀɴɴᴇʟ❗️**"
        else:
            clone_bot = temp.CLONE_BOTS.get(query.from_user.id)
            chat = await clone_bot.get_chat(settings['log_channel'])
            channel = f"ʏᴏᴜʀ ʟᴏɢ ᴄʜᴀɴɴᴇʟ - {chat.title}"
        await query.message.edit(f"<b>ᴡʜᴀᴛ ɪs ʟᴏɢ ᴄʜᴀɴɴᴇʟ ??\n\nɪꜰ ɴᴇᴡ ᴜsᴇʀs sᴛᴀʀᴛ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ ᴛʜᴇɴ ʙᴏᴛ ɴᴏᴛɪꜰɪᴇs ʏᴏᴜ\n\n{channel}</b>", reply_markup=InlineKeyboardMarkup(btn))
    elif query.data.startswith("bot_update_req_fsub"):
        _, bot_id, status = query.data.split("#")
        settings = await db.get_bot_settings(int(bot_id))
        if settings['force_channel'] == "":
            await query.answer("ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ.", show_alert=True)
            return
        if status == 'True':
            await db.update_bot_settings(int(bot_id), 'req_fsub', False)
        else:
            await db.update_bot_settings(int(bot_id), 'req_fsub', True)
        settings = await db.get_bot_settings(int(bot_id))
        btn = [[
            InlineKeyboardButton('sᴇᴛ ᴄʜᴀɴɴᴇʟ ', callback_data=f'bot_set_force_channel#{bot_id}'),
            InlineKeyboardButton('ᴅᴇʟᴇᴛᴇ ᴄʜᴀɴɴᴇʟ', callback_data=f'bot_force_channel_delete#{bot_id}')
        ],[
            InlineKeyboardButton('ᴏꜰꜰ req fsub' if settings['req_fsub'] else 'ᴏɴ req fsub', callback_data=f"bot_update_req_fsub#{bot_id}#{settings['req_fsub']}"),
            InlineKeyboardButton('ᴏꜰꜰ sᴜʙsᴄʀɪʙᴇ' if settings['force_subscribe'] else 'ᴏɴ sᴜʙsᴄʀɪʙᴇ', callback_data=f"bot_update_force_subscribe#{bot_id}#{settings['force_subscribe']}")
        ],[
            InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data=f'bot_settings#{bot_id}')
        ]]
        req_fsubs = 'ᴏɴ ✅' if settings['req_fsub'] else 'ᴏꜰꜰ ❌'
        subscribe = 'ᴏɴ ✅' if settings['force_subscribe'] else 'ᴏꜰꜰ ❌'
        if settings['force_channel'] == "":
            channel = "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ."
        else:
            clone_bot = temp.CLONE_BOTS.get(query.from_user.id)
            chat = await clone_bot.get_chat(settings['force_channel'])
            channel = f"ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ - {chat.title}"
        await query.message.edit(f"<b>ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟ ɪɴ ɢɪᴠᴇ ꜰɪʟᴇs.\n\nsᴜʙsᴄʀɪʙᴇ - {subscribe}\nRᴇQᴜᴇꜱᴛ Fꜱᴜʙ - {req_fsubs}\n\n{channel}</b>", reply_markup=InlineKeyboardMarkup(btn))
    elif query.data.startswith("bot_set_log_channel"):
        _, bot_id = query.data.split("#")
        bot = await db.get_bot(int(bot_id))
        btn = [[
            InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data=f'bot_log_channel_setgs#{bot_id}')
        ]]
        await query.message.edit_text(f"<b>ꜰᴏʀᴡᴀʀᴅ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴛᴏ ᴍᴇ,\nᴀɴᴅ ᴍᴀᴋᴇ sᴜʀᴇ @{bot['username']} ɪs ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ.\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss.</b>")
        msg = await client.listen(query.from_user.id)
        if msg.text == '/cancel':
            await query.message.delete()
            await query.message.reply("**ᴄᴀɴᴄᴇʟᴇᴅ ᴛʜɪs ᴘʀᴏᴄᴇss...**", reply_markup=InlineKeyboardMarkup(btn))
            return
        if msg.forward_from_chat and msg.forward_from_chat.type == enums.ChatType.CHANNEL:
            chat_id = msg.forward_from_chat.id
        else:
            await query.message.delete()
            await query.message.reply('**ɴᴏᴛ ꜰᴏʀᴡᴀʀᴅ ꜰʀᴏᴍ ᴄʜᴀɴɴᴇʟ**', reply_markup=InlineKeyboardMarkup(btn))
            return
        clone_bot = temp.CLONE_BOTS.get(query.from_user.id)
        await query.message.delete()
        try:
            chat = await clone_bot.get_chat(chat_id)
            t = await clone_bot.send_message(chat.id, 'Test!')
            await t.delete()
        except Exception as e:
            await query.message.reply(f'**💔 sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ...**\n\n<code>{e}</code>', reply_markup=InlineKeyboardMarkup(btn))
            return
        await db.update_bot_settings(int(bot_id), 'log_channel', chat.id)
        await query.message.reply(f"**⚡️ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴀᴅᴅᴇᴅ ʏᴏᴜʀ ʟᴏɢ ᴄʜᴀɴɴᴇʟ** - {chat.title}", reply_markup=InlineKeyboardMarkup(btn))
    elif query.data.startswith("bot_admin_setgs"):
        _, bot_id = query.data.split("#")
        settings = await db.get_bot_settings(int(bot_id))
        admin_ids = settings.get('admin_ids', [])
        admins_list = []
        for admin_id in admin_ids:
            user = await get_clone_bot_user(bot_id, admin_id)
            user_name = user.get("name", "Unknown") if user else "Unknown User"
            admins_list.append(f"• {user_name} ({admin_id})")
        admins_display = "\n".join(admins_list) if admins_list else "<b>Tʜᴇʀᴇ Aʀᴇ Nᴏ Aᴅᴍɪɴs Yᴇᴛ.</b>"
        btn = [[
            InlineKeyboardButton('➕ Aᴅᴅ Aᴅᴍɪɴ', callback_data=f'bot_add_admin#{bot_id}'),
            InlineKeyboardButton('➖ Rᴇᴍᴏᴠᴇ Aᴅᴍɪɴ', callback_data=f'bot_remove_admin#{bot_id}')
        ],[
            InlineKeyboardButton('≼ Bᴀᴄᴋ', callback_data=f'bot_settings#{bot_id}')
        ]]
        await query.message.edit(f"<b>Aᴅᴍɪɴ Hᴀᴠᴇ Aᴄᴄᴇꜱꜱ Tᴏ ᴀʟʟ Yᴏᴜʀ Cʟᴏɴᴇ Fᴇᴀᴛᴜʀᴇꜱ, Iɴᴄʟᴜᴅᴇ Bʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ.\n\nCᴜʀʀᴇɴᴛ Aᴅᴍɪɴs:\n\n{admins_display}</b>", reply_markup=InlineKeyboardMarkup(btn))
    elif query.data.startswith("bot_add_admin"):
        _, bot_id = query.data.split("#")
        btn = [[
            InlineKeyboardButton('≼ Bᴀᴄᴋ', callback_data=f'bot_admin_setgs#{bot_id}')
        ]]
        await query.message.edit_text("<b>Sᴇɴᴅ Mᴇ Tʜᴇ Usᴇʀ Iᴅ Tᴏ Aᴅᴅ As Aɴ Aᴅᴍɪɴ.\n\n/cancel - Cᴀɴᴄᴇʟ Tʜɪs Pʀᴏᴄᴇss.</b>")
        msg = await client.listen(query.from_user.id)
        if msg.text == '/cancel':
            await query.message.delete()
            await query.message.reply("<b>Cᴀɴᴄᴇʟʟᴇᴅ Tʜɪs Pʀᴏᴄᴇss...</b>", reply_markup=InlineKeyboardMarkup(btn))
            return
        if not msg.text.isdigit():
            await query.message.delete()
            await query.message.reply("<b>⚠️ Iɴᴠᴀʟɪᴅ Usᴇʀ Iᴅ.</b>", reply_markup=InlineKeyboardMarkup(btn))
            return
        admin_id = int(msg.text)
        user = await get_clone_bot_user(bot_id, admin_id)
        if not user:
            await query.message.edit_text("<b>⚠️ Tʜᴇ Usᴇʀ Hᴀs Nᴏᴛ Sᴛᴀʀᴛᴇᴅ Tʜᴇ Cʟᴏɴᴇ Bᴏᴛ Yᴇᴛ.\n\nPʟᴇᴀsᴇ Mᴀᴋᴇ Sᴜʀᴇ Tʜᴇ Usᴇʀ Sᴛᴀʀᴛs Tʜᴇ Bᴏᴛ Bᴇꜰᴏʀᴇ Pʀᴏᴄᴇᴇᴅɪɴɢ.</b>", reply_markup=InlineKeyboardMarkup(btn))
            return
        user_name = user.get("name", "Unknown")
        settings = await db.get_bot_settings(int(bot_id))
        admin_ids = settings.get('admin_ids', [])
        if admin_id in admin_ids:
            await query.message.delete()
            await query.message.reply("<b>⚠️ Usᴇʀ Iᴅ Aʟʀᴇᴀᴅʏ Exɪsᴛs.</b>", reply_markup=InlineKeyboardMarkup(btn))
            return
        admin_ids.append(admin_id)
        await db.update_bot_settings(int(bot_id), 'admin_ids', admin_ids)
        await query.message.delete()
        await query.message.reply("<b>✅ Aᴅᴍɪɴ Aᴅᴅᴇᴅ Sᴜᴄᴄᴇssꜰᴜʟʟʏ.</b>", reply_markup=InlineKeyboardMarkup(btn))
    elif query.data.startswith("bot_remove_admin"):
        _, bot_id = query.data.split("#")
        btn = [[
            InlineKeyboardButton('≼ Bᴀᴄᴋ', callback_data=f'bot_admin_setgs#{bot_id}')
        ]]
        settings = await db.get_bot_settings(int(bot_id))
        admin_ids = settings.get('admin_ids', [])
        if not admin_ids:
            await query.answer("Tʜᴇʀᴇ Aʀᴇ Nᴏ Aᴅᴍɪɴs Tᴏ Rᴇᴍᴏᴠᴇ.", show_alert=True)
            return
        await query.message.edit_text("<b>Sᴇɴᴅ Mᴇ Tʜᴇ Usᴇʀ Iᴅ Tᴏ Rᴇᴍᴏᴠᴇ Fʀᴏᴍ Aᴅᴍɪɴs.\n\n/cancel - Cᴀɴᴄᴇʟ Tʜɪs Pʀᴏᴄᴇss.</b>")
        msg = await client.listen(query.from_user.id)
        if msg.text == '/cancel':
            await query.message.delete()
            await query.message.reply("<b>Cᴀɴᴄᴇʟʟᴇᴅ Tʜɪs Pʀᴏᴄᴇss...</b>", reply_markup=InlineKeyboardMarkup(btn))
            return
        if not msg.text.isdigit():
            await query.message.delete()
            await query.message.reply("<b>⚠️ Iɴᴠᴀʟɪᴅ Usᴇʀ Iᴅ.</b>", reply_markup=InlineKeyboardMarkup(btn))
            return
        admin_id = int(msg.text)
        if admin_id not in admin_ids:
            await query.message.delete()
            await query.message.reply("<b>⚠️ Usᴇʀ Iᴅ Nᴏᴛ Fᴏᴜɴᴅ Iɴ Aᴅᴍɪɴs.</b>", reply_markup=InlineKeyboardMarkup(btn))
            return
        admin_ids.remove(admin_id)
        await db.update_bot_settings(int(bot_id), 'admin_ids', admin_ids)
        await query.message.delete()
        await query.message.reply("<b>✅ Aᴅᴍɪɴ Rᴇᴍᴏᴠᴇᴅ Sᴜᴄᴄᴇssꜰᴜʟʟʏ.</b>", reply_markup=InlineKeyboardMarkup(btn))
#----------------------------------------------------------------------- AUTO FILTER PREMIUM ----------------------------------------------------------------------------#
    elif query.data.startswith("bot_prime_setgs"):
        _, bot_id = query.data.split("#")
        settings = await db.get_bot_settings(int(bot_id))
        btn = [[
            InlineKeyboardButton('🏷️ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴘᴇxᴛ 🏷️', callback_data=f'bot_prime_text#{bot_id}')
        ],[
            InlineKeyboardButton('➕ ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ➕', callback_data=f"bot_add_premium#{bot_id}")
        ],[
            InlineKeyboardButton('➖ ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ➖', callback_data=f'remove_prmuser#{bot_id}')
        ],[
            InlineKeyboardButton('🔐 ᴘʀᴇᴍɪᴜᴍ ᴍᴏᴅᴇ ɪꜱ Oɴ ✔' if settings['premium_mode'] else '🔐 ᴘʀᴇᴍɪᴜᴍ ᴍᴏᴅᴇ ɪꜱ Oғғ ✘', callback_data=f"bot_prime_on_setgs#{bot_id}#{settings['premium_mode']}")
        ],[
            InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data=f'bot_settings#{bot_id}')
        ]]
        status = 'ᴏɴ ✅' if settings['premium_mode'] else 'ᴏꜰꜰ ❌'
        await query.message.edit(f"<b>ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ sᴇᴛᴛɪɴɢs ʜᴇʀᴇ. \n\nᴛʜɪs ғᴇᴀᴛᴜʀᴇ ᴡᴏʀᴋ ᴏɴʟʏ ᴡʜᴇɴ ʟɪɴᴋ sʜᴏʀᴛɴᴇʀ ɪs ᴇɴᴀʙʟᴇᴅ\n\nᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs - {status}</b>", reply_markup=InlineKeyboardMarkup(btn))
    
    elif query.data.startswith("bot_prime_on_setgs"):
        _, bot_id, status = query.data.split("#")
        settings = await db.get_bot_settings(int(bot_id))
        if status == 'True':
            await db.update_bot_settings(int(bot_id), 'premium_mode', False)
        else:
            await db.update_bot_settings(int(bot_id), 'premium_mode', True)
        crazy = [[
            InlineKeyboardButton('🏷️ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴛᴇxᴛ 🏷️', callback_data=f'bot_prime_text#{bot_id}')
        ],[
            InlineKeyboardButton('➕ ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ➕', callback_data=f"bot_add_premium#{bot_id}")
        ],[
            InlineKeyboardButton('➖ ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ➖', callback_data=f'remove_prmuser#{bot_id}')
        ],[
            InlineKeyboardButton('🔐 ᴘʀᴇᴍɪᴜᴍ ᴍᴏᴅᴇ ɪꜱ Oɴ ✔' if settings['premium_mode'] else '🔐 ᴘʀᴇᴍɪᴜᴍ ᴍᴏᴅᴇ ɪꜱ Oғғ ✘', callback_data=f"bot_prime_on_setgs#{bot_id}#{settings['premium_mode']}")
        ],[
            InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data=f'bot_settings#{bot_id}')
        ]]
        status = 'ᴏɴ ✅' if settings['premium_mode'] else 'ᴏꜰꜰ ❌'
        await query.message.edit(f"<b>ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ sᴇᴛᴛɪɴɢs ʜᴇʀᴇ. \n\nᴛʜɪs ғᴇᴀᴛᴜʀᴇ ᴡᴏʀᴋ ᴏɴʟʏ ᴡʜᴇɴ ʟɪɴᴋ sʜᴏʀᴛɴᴇʀ ɪs ᴇɴᴀʙʟᴇᴅ\n\nᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs - {status}</b>", reply_markup=InlineKeyboardMarkup(crazy))
    
    elif query.data.startswith("bot_prime_text"):
        _, bot_id = query.data.split("#")
        btn = [[
            InlineKeyboardButton('≼ Bᴀᴄᴋ', callback_data=f'bot_prime_setgs#{bot_id}')
        ]]
        await query.message.edit_text("sᴇɴᴅ ᴍᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴛᴇxᴛ.\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss.")
        msg = await client.listen(query.from_user.id)
        if msg.text == '/cancel':
            await query.message.delete()
            await query.message.reply("ᴄᴀɴᴄᴇʟʟᴇᴅ ᴛʜɪs ᴘʀᴏᴄᴇss...", reply_markup=InlineKeyboardMarkup(btn))
            return
        try:
            msg.text.format(mention='mention', chat_title='chat_title')
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'ᴡʀᴏɴɢ ꜰᴏʀᴍᴀᴛ <code>{e}</code> ᴜsᴇᴅ.', reply_markup=InlineKeyboardMarkup(btn))
            return
        await db.update_bot_settings(int(bot_id), 'premium_text', msg.text)
        await query.message.delete()
        await query.message.reply(f"sᴜᴄᴄᴇssꜰᴜʟʟʏ sᴇᴛ ᴘʀᴇᴍɪᴜᴍ ᴛᴇxᴛ -\n\n{msg.text}", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(btn))
        
    elif query.data.startswith("remove_prmuser"):
        _, bot_id = query.data.split("#")
        btn = [[InlineKeyboardButton('≼ Bᴀᴄᴋ', callback_data=f'bot_prime_setgs#{bot_id}')]]
        await query.message.edit_text(
            "<b>Sᴇɴᴅ Mᴇ Tʜᴇ Usᴇʀ Iᴅ Tᴏ Rᴇᴍᴏᴠᴇ.\n\n/cancel - Cᴀɴᴄᴇʟ Tʜɪs Pʀᴏᴄᴇss.</b>"
        )
        msg = await client.listen(query.from_user.id)
        if msg.text == '/cancel':
            return await query.message.reply("<b>Cᴀɴᴄᴇʟʟᴇᴅ Tʜɪs Pʀᴏᴄᴇss...</b>", reply_markup=InlineKeyboardMarkup(btn))
        if not msg.text.isdigit():
            return await query.message.reply("<b>⚠️ Iɴᴠᴀʟɪᴅ Usᴇʀ Iᴅ.</b>", reply_markup=InlineKeyboardMarkup(btn))
        user_id = int(msg.text)
        await remove_premium(user_id, int(bot_id))
        user_id = int(msg.text)
        clone_bot = temp.CLONE_BOTS.get(query.from_user.id)
        await clone_bot.send_message(chat_id=user_id, text=f"<b>ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ʜᴀꜱ ʙᴇᴇɴ ᴇxᴘɪʀᴇᴅ.</b>")
        await query.message.delete()
        await query.message.reply("<b>✅ ᴘʀᴇᴍɪᴜᴍ Rᴇᴍᴏᴠᴇᴅ Sᴜᴄᴄᴇssꜰᴜʟʟʏ.</b>", reply_markup=InlineKeyboardMarkup(btn))
            
    elif query.data.startswith("bot_add_premium"):
        _, bot_id = query.data.split("#")
        btn = [[
            InlineKeyboardButton('≼ Bᴀᴄᴋ', callback_data=f'bot_prime_setgs#{bot_id}')
        ]]
        await query.message.edit_text("<b>Sᴇɴᴅ Mᴇ Tʜᴇ Usᴇʀ Iᴅ Tᴏ Aᴅᴅ As Aɴ Aᴅᴍɪɴ.\n\n/cancel - Cᴀɴᴄᴇʟ Tʜɪs Pʀᴏᴄᴇss.</b>")
        msg = await client.listen(query.from_user.id)
        if msg.text == '/cancel':
            await query.message.delete()
            await query.message.reply("<b>Cᴀɴᴄᴇʟʟᴇᴅ Tʜɪs Pʀᴏᴄᴇss...</b>", reply_markup=InlineKeyboardMarkup(btn))
            return
        if not msg.text.isdigit():
            await query.message.delete()
            await query.message.reply("<b>⚠️ Iɴᴠᴀʟɪᴅ Usᴇʀ Iᴅ.</b>", reply_markup=InlineKeyboardMarkup(btn))
            return
        user_id = int(msg.text)
        buttons = [
            [InlineKeyboardButton("1 ᴡᴇᴇᴋ", callback_data=f"add_premium#{bot_id}#{user_id}#7days")],
            [InlineKeyboardButton("15 ᴅᴀʏꜱ", callback_data=f"add_premium#{bot_id}#{user_id}#15days")],
            [InlineKeyboardButton("1 ᴍᴏɴᴛʜ", callback_data=f"add_premium#{bot_id}#{user_id}#30days")],
            [InlineKeyboardButton("2 ᴍᴏɴᴛʜꜱ", callback_data=f"add_premium#{bot_id}#{user_id}#60days")],
        ]
        await query.message.reply("<b>ᴄʜᴏᴏꜱᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ.</b>", reply_markup=InlineKeyboardMarkup(buttons))
            
    elif query.data.startswith("bot_update_active"):
        _, bot_id, status = query.data.split("#")
        btn = [[InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data=f'bot_settings#{bot_id}')]]
        if status == 'True':
            clone_bot = temp.CLONE_BOTS.get(query.from_user.id)
            try:
                await clone_bot.stop()
            except Exception as e:
                return await query.message.edit(f'<b>💔 sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ...\n\n<code>{e}</code></b>', reply_markup=InlineKeyboardMarkup(btn))
            await db.update_bot_settings(int(bot_id), 'is_active', False)
            await query.message.edit("<b>sᴜᴄᴄᴇssꜰᴜʟ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ ✅</b>", reply_markup=InlineKeyboardMarkup(btn))
        else:
            clone_bot = temp.CLONE_BOTS.get(query.from_user.id)
            await query.message.edit('sᴛᴀʀᴛɪɴɢ ʙᴏᴛ...')
            try:
                await clone_bot.start()
            except Exception as e:
                return await query.message.edit(f'💔 sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ...\n\n<code>{e}</code>', reply_markup=InlineKeyboardMarkup(btn))
            temp.CLONE_BOTS_START_TIME[int(bot_id)] = time.time()
            await db.update_bot_settings(int(bot_id), 'is_active', True)
            await query.message.edit("**sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴀᴄᴛɪᴠᴀᴛᴇᴅ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ ♻️**", reply_markup=InlineKeyboardMarkup(btn))

    
