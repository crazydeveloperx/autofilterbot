import os
import pytz
import logging
import random
import string
import asyncio
import time
from Script import script
from datetime import datetime, timedelta
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait, MessageTooLong, RPCError
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils import get_size, get_time, temp, is_clone_bot_force_subscribed, get_clone_bot_shortlink, get_seconds
from database.db import db
from info import *
from psutil import virtual_memory, disk_usage, cpu_percent
from pymongo import MongoClient
from clone_database.users_db import *
from clone_database.premium import update_user, is_premium_user, get_premium_details, remove_premium, get_clone_bot_users_prm_count, get_clone_bot_all_prm_users
from clone_database.files_db import get_clone_bot_files_count, get_clone_bot_file_details
from database.files_db import total_files_count, get_file_details
from plugins.ads import *
from plugins.database import ub

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type != enums.ChatType.PRIVATE:
        return await message.reply("<b>ʏᴇs, ɪ ᴀᴍ ᴏɴʟɪɴᴇ 😁\nᴡʜʏ ʏᴏᴜ sᴛᴀʀᴛ ᴍᴇ 🥱</b>")

    me = await client.get_me()
    tz = pytz.timezone('Asia/Colombo')
    await db.update_bot_last_used(me.id, datetime.now(tz))
    settings = await db.get_bot_settings(me.id)
    added = await clone_bot_add_user(me.id, message.from_user.id, message.from_user.first_name)
    user_id = message.from_user.id
    bot = await db.get_bot(me.id)
    admin = bot['_id']
    has_premium = await ub.has_premium_access(admin)
    is_premium = await is_premium_user(user_id, me.id)
    if settings['log_channel'] != "" and added:
        text = """<b>#New_Bot_User
        
» ɴᴀᴍᴇ - {}
» ɪᴅ - <code>{}</code></b>"""
        await client.send_message(settings['log_channel'], text.format(message.from_user.mention, message.from_user.id))

    footer_text = await get_footer_text()
    footer = f"\n<b>━━━━━━━━━━━━━━━━━━\n<i>Ads:</i> {footer_text}\n━━━━━━━━━━━━━━━━━━</b>" if footer_text and not has_premium else ""

    if len(message.command) == 2 and message.command[1].startswith('file'):
        _, file_unique_id = message.command[1].split("_")
        file = await get_file_details(file_unique_id)
        
        if not file:
            return await message.reply('<b>ꜰɪʟᴇs ɴᴏᴛ ꜰᴏᴜɴᴅ 😢</b>')

        if settings['force_subscribe'] and not await is_clone_bot_force_subscribed(client, settings['force_channel'], message.from_user.id) and not await find_join_req(me.id, settings['force_channel'], message.from_user.id):
            if 'req_fsub' not in settings:
                settings['req_fsub'] = False
                req_fsub = settings['req_fsub']
            if settings['req_fsub']:
                link = await client.create_chat_invite_link(settings['force_channel'], creates_join_request=True)
            else:
                link = await client.create_chat_invite_link(settings['force_channel'])
            try_link = f"https://telegram.me/{me.username}?start=file_{file['_id']}"
            buttons = [[
                InlineKeyboardButton("⛔️ ᴊᴏɪɴ ɴᴏᴡ ⛔️", url=link.invite_link)
            ],[
                InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", url=try_link)
            ]]
            await message.reply("<b>🫵 ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʀʏ ᴀɢᴀɪɴ ʙᴜᴛᴛᴏɴ 👇</b>", reply_markup=InlineKeyboardMarkup(buttons))
            return
            
        if not is_premium and settings['shortlink']:
            btn = [[
                InlineKeyboardButton('📥 ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ 📥', url=await get_clone_bot_shortlink(me.id, f"https://telegram.me/{me.username}?start=shortlink_{file['_id']}"))
            ]]
            if settings['tutorial'] != "":
                btn.append([
                    InlineKeyboardButton('⁉️ ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ ⁉️', url=settings['tutorial'])
                ])
            if settings['premium_mode']:
                btn.append([InlineKeyboardButton('😁 ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ - ʀᴇᴍᴏᴠᴇ ᴀᴅꜱ 😁', callback_data='get_plan')])
            await message.reply(f"<code>{file['file_name']}</code>\n\n<b>✅ ʏᴏᴜʀ ꜰɪʟᴇ ɪ𝘴 ʀᴇᴀᴅʏ,\nᴘʟᴇᴀ𝘴ᴇ ᴅᴏᴡɴʟᴏᴀᴅ ᴜ𝘴ɪɴɢ ᴛʜɪ𝘴 ʟɪɴᴋ...</b>", reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
            return
            
        wait_msg = await message.reply("<b>🕐 ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔞 Study Material', url="https://t.me/+G3jcp4KdWdY4MjQ1")]]) if not has_premium else None)
        sent_msg = None
        retries = 5
        for attempt in range(retries):
            try:
                sent_msg = await temp.BOT.send_cached_media(chat_id=FILES_CHANNEL, file_id=file['file_id'])
                break
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except OSError:
                if attempt < retries - 1:
                    await asyncio.sleep(5)  # Wait for 5 seconds before retrying
                else:
                    raise
            except RPCError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                else:
                    raise
            await asyncio.sleep(1)

        if not sent_msg:
            return await message.reply('<b>ꜱᴏʀʀʏ, ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ 😢</b>') 
        
        msg = await client.get_messages(FILES_CHANNEL, sent_msg.id)
        media = getattr(msg, msg.media.value)
        file_id = media.file_id
        caption = settings['file_caption'].format(
            file_name = file['file_name'],
            file_size = get_size(file['file_size'])
        ) + footer
            
        crazy = [] 
        if 'file_button_text' in settings and settings['file_button_text'] and 'file_button_url' in settings and settings['file_button_url']:
            crazy.append([
                InlineKeyboardButton(settings['file_button_text'], url=settings['file_button_url'])
            ])
        vks = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=crazy) if crazy else None
        )
        await asyncio.sleep(3)
        await wait_msg.delete()
        if settings['file_auto_delete']:
            k = await message.reply(f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{get_time(settings['file_auto_delete_time']).lower()}</u> <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</i></b>")
            await asyncio.sleep(settings['file_auto_delete_time'])
            await vks.delete()
            await k.delete()
                
    elif len(message.command) == 2 and message.command[1].startswith('shortlink'):
        _, file_unique_id = message.command[1].split("_")
        file = await get_file_details(file_unique_id)
        
        if not file:
            return await message.reply('<b>ꜰɪʟᴇs ɴᴏᴛ ꜰᴏᴜɴᴅ 😢</b>')

        if settings['force_subscribe'] and not await is_clone_bot_force_subscribed(client, settings['force_channel'], message.from_user.id) and not await find_join_req(me.id, settings['force_channel'], message.from_user.id):
            if 'req_fsub' not in settings:
                settings['req_fsub'] = False
                req_fsub = settings['req_fsub']
            if settings['req_fsub']:
                link = await client.create_chat_invite_link(settings['force_channel'], creates_join_request=True)
            else:
                link = await client.create_chat_invite_link(settings['force_channel'])
            try_link = f"https://telegram.me/{me.username}?start=file_{file['_id']}"
            buttons = [[
                InlineKeyboardButton("⛔️ ᴊᴏɪɴ ɴᴏᴡ ⛔️", url=link.invite_link)
            ],[
                InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", url=try_link)
            ]]
            await message.reply("<b>🫵 ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʀʏ ᴀɢᴀɪɴ ʙᴜᴛᴛᴏɴ 👇</b>", reply_markup=InlineKeyboardMarkup(buttons))
            return
            
        wait_msg = await message.reply("<b>🕐 ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔞 Study Material', url="https://t.me/+G3jcp4KdWdY4MjQ1")]]) if not has_premium else None)
        sent_msg = None
        retries = 5
        for attempt in range(retries):
            try:
                sent_msg = await temp.CRAZY.send_cached_media(chat_id=FILES_CHANNEL2, file_id=file['file_id'])
                break
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except OSError:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                else:
                    raise
            except RPCError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                else:
                    raise
            await asyncio.sleep(1)

        if not sent_msg:
            return await message.reply('<b>ꜱᴏʀʀʏ, ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ 😢</b>')    
        
        msg = await client.get_messages(FILES_CHANNEL2, sent_msg.id)
        media = getattr(msg, msg.media.value)
        file_id = media.file_id
        caption = settings['file_caption'].format(
            file_name = file['file_name'],
            file_size = get_size(file['file_size'])
        ) + footer
        crazy = [] 
    
        if 'file_button_text' in settings and settings['file_button_text'] and 'file_button_url' in settings and settings['file_button_url']:
            crazy.append([
                InlineKeyboardButton(settings['file_button_text'], url=settings['file_button_url'])
            ])
        vks = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=crazy) if crazy else None
        )
        await asyncio.sleep(3)
        await wait_msg.delete()
        if settings['file_auto_delete']:
            k = await message.reply(f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{get_time(settings['file_auto_delete_time']).lower()}</u> <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</i></b>")
            await asyncio.sleep(settings['file_auto_delete_time'])
            await vks.delete()
            await k.delete()
    else:
        message_text = settings['start_text'].format(mention=message.from_user.mention)
        buttons = [[
            InlineKeyboardButton('⇄ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⇆', url=f'http://t.me/{me.username}?startgroup=start')
        ],[
            InlineKeyboardButton('⚠️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ 📚', callback_data='about')
        ]]
        if 'button_text' in settings and settings['button_text'] and 'button_url' in settings and settings['button_url']:
            buttons.append([
                InlineKeyboardButton(settings['button_text'], url=settings['button_url'])
            ])
        if has_premium and settings.get('sec_button_text') and settings.get('sec_button_url'):
            buttons.append([
                InlineKeyboardButton(settings['sec_button_text'], url=settings['sec_button_url'])
            ])
        if settings['start_pic'] == "":
            await message.reply(text=message_text, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await message.reply_photo(photo=settings['start_pic'], caption=message_text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command('id'))
async def show_id(client, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text(f"» ᴜsᴇʀ ɪᴅ - <code>{message.from_user.id}</code>")

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply_text(f"» ɢʀᴏᴜᴘ ɪᴅ - <code>{message.chat.id}</code>")

    elif chat_type == enums.ChatType.CHANNEL:
        await message.reply_text(f'» ᴄʜᴀɴɴᴇʟ ɪᴅ - <code>{message.chat.id}</code>')


@Client.on_message(filters.private & filters.command('users'))
async def list_users(client, message):
    me = await client.get_me()
    bot = await db.get_bot(me.id)
    settings = await db.get_bot_settings(me.id)
    admin_ids = settings.get("admin_ids", [])
    if bot['_id'] != message.from_user.id and message.from_user.id not in admin_ids:
        return
    msg = await message.reply('<b>ᴄᴀʟᴄᴜʟᴀᴛɪɴɢ...</b>')
    users = await get_clone_bot_all_users(me.id)
    total = await get_clone_bot_users_count(me.id)
    out = "sᴀᴠᴇᴅ ᴜsᴇʀs -\n\n"
    for user in users:
        out += f"» ɴᴀᴍᴇ - {user['name']}\n» ɪᴅ - {user['_id']}"
        out += '\n\n'
    out += f"» ᴛᴏᴛᴀʟ ᴜsᴇʀs - {total}"
    try:
        await msg.edit(out)
    except MessageTooLong:
        with open('Users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('Users.txt')
        await msg.delete()

@Client.on_message(filters.command('stats'))
async def status(client, message):
    me = await client.get_me()
    bot = await db.get_bot(me.id)
    text = """<b><u>Current Bot Stats:</u>
    
🗂 ꜰɪʟᴇs - <code>{}</code>
👤 ᴜsᴇʀs - <code>{}</code>
💤 ᴜᴘᴛɪᴍᴇ - <code>{}</code>
⏰ ᴛɪᴍᴇꜱᴛᴀᴍᴘ : <code>{}</code></b>"""
    msg = await message.reply('<b>ᴄᴀʟᴄᴜʟᴀᴛɪɴɢ...</b>')
    me = await client.get_me()
    files = await total_files_count()
    settings = await db.get_bot_settings(me.id)
    users = await get_clone_bot_users_count(me.id)
    uptime = get_time(time.time() - temp.CLONE_BOTS_START_TIME.get(me.id))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    btn = [
        [InlineKeyboardButton('🗼 ʜᴏᴍᴇ', callback_data='start'),
         InlineKeyboardButton('ʀᴇꜰʀᴇꜱʜ ♻️', callback_data='status')
    ]]
    keyboard = InlineKeyboardMarkup(btn)
    await msg.edit(text.format(files, users, uptime, timestamp), reply_markup=keyboard)
