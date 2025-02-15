from info import API_ID, API_HASH, LOG_CHANNEL, ADMINS
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, CallbackQuery
from utils import *
from database.db import db
import re
import pytz
from pyrogram.errors import InputUserDeactivated, AccessTokenExpired, AccessTokenInvalid, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from datetime import datetime
import asyncio
from Script import script
import time

@Client.on_message(filters.private & filters.command('frestart') & filters.user(ADMINS))
async def frestart(client, message):
    msg = await message.reply('🔄 Restarting bots, please wait...')
    
    bots = await db.get_all_bots()
    for bot in bots:
        await restart_clone_bot(bot)
        
    await msg.edit("✅ All eligible bots have been restarted successfully!")

@Client.on_message(filters.command('clone_auto'))
async def clone_menu(client, message):
    if message.chat.type != enums.ChatType.PRIVATE:
        btn = [[
            InlineKeyboardButton("+ ᴏᴘᴇɴ ɪɴ ᴘᴍ +", url=f'http://t.me/{temp.BOT_USERNAME}?start=clone')
        ]]
        return await message.reply('<b>ᴘʟᴇᴀsᴇ ᴏᴘᴇɴ ᴄʟᴏɴᴇ ᴍᴇɴᴜ ɪɴ ᴘᴍ 😢</b>', reply_markup=InlineKeyboardMarkup(btn))

    bot_found = await db.is_bot_found_using_user(message.from_user.id)
    if bot_found:
        bot = await db.get_bot_from_user(message.from_user.id)
        settings = await db.get_bot_settings(bot['bot_id'])
        buttons = [[
            InlineKeyboardButton('sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ', callback_data=f"bot_start_message_setgs#{bot['bot_id']}"),
            InlineKeyboardButton('ɪᴍᴅʙ', callback_data=f"bot_imdb_setgs#{bot['bot_id']}"),
        ],[
            InlineKeyboardButton('ᴍᴀx ʀᴇsᴜʟᴛs', callback_data=f"bot_max_results_setgs#{bot['bot_id']}"),
            InlineKeyboardButton('ʀᴇsᴜʟᴛ ᴍᴏᴅᴇ', callback_data=f"c_files_mode#{bot['bot_id']}")
        ],[
            InlineKeyboardButton('ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ', callback_data=f"bot_caption_setgs#{bot['bot_id']}"),
            InlineKeyboardButton('ᴘᴍ ꜱᴇᴀʀᴄʜ', callback_data=f"bot_pm_search_setgs#{bot['bot_id']}")
        ],[
            InlineKeyboardButton('ꜰɪʟᴛᴇʀ ᴅᴇʟ ᴛɪᴍᴇ', callback_data=f"bot_auto_delete_setgs#{bot['bot_id']}"),
            InlineKeyboardButton('ꜰɪʟᴇ ᴅᴇʟ ᴛɪᴍᴇ', callback_data=f"bot_file_auto_delete_setgs#{bot['bot_id']}")
        ],[
            InlineKeyboardButton('sʜᴏʀᴛ ʟɪɴᴋ', callback_data=f"bot_shortlink_setgs#{bot['bot_id']}"),
            InlineKeyboardButton('ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ', callback_data=f"bot_tutorial_setgs#{bot['bot_id']}")
        ],[
            InlineKeyboardButton('ꜰᴏʀᴄᴇ ᴄʜᴀɴɴᴇʟ', callback_data=f"bot_force_channel_setgs#{bot['bot_id']}"),
            InlineKeyboardButton('ʟᴏɢ ᴄʜᴀɴɴᴇʟ', callback_data=f"bot_log_channel_setgs#{bot['bot_id']}") 
        ],[
            InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', callback_data=f"bot_update_setgs#{bot['bot_id']}"),
            InlineKeyboardButton('ᴍᴏɴɢᴏ ᴅʙ', callback_data=f"bot_mongodb_setgs#{bot['bot_id']}")
        ],[
            InlineKeyboardButton('ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇ ʙᴏᴛ' if settings['is_active'] else 'ᴀᴄᴛɪᴠᴀᴛᴇ ʙᴏᴛ', callback_data=f"bot_update_active#{bot['bot_id']}#{settings['is_active']}"),
            InlineKeyboardButton('ᴅᴇʟᴇᴛᴇ ʙᴏᴛ', callback_data='bot_delete')
        ],[
            InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data=f'close#{message.from_user.id}')
        ]]
        used = await db.get_bot_last_used(bot['bot_id'])
        tz = pytz.timezone('Asia/Colombo')
        last_used = get_time((datetime.now(tz) - used.astimezone(tz)).total_seconds())
        await message.reply(f"<b>🤖 <u>Bᴏᴛ Dᴇᴛᴀɪʟs:</u>\n\n✦ ᴜsᴇʀɴᴀᴍᴇ : @{bot['username']}\n✦ ꜱᴛᴀᴛᴜꜱ : <code>{'ᴀᴄᴛɪᴠᴀᴛᴇ ✅' if settings['is_active'] else 'ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇ ❌'}</code>\n✦ ʟᴀsᴛ ᴜsᴇᴅ ᴏɴ : <code>{last_used}</code> ᴀɢᴏ\n\n<u>Nᴏᴛᴇ :</u> <i>ɪꜰ ᴄʟᴏɴᴇ ʙᴏᴛ ɴᴏᴛ ᴜsɪɴɢ ᴀʟᴏɴɢ ᴏɴᴇ ᴡᴇᴇᴋ ᴛʜᴇɴ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴄʟᴏɴᴇ ʙᴏᴛ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇ.</i>\n\n🦊 Mᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ ›› <a href=https://t.me/Crazybotz>cRAZY BoTZ</a></b>", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        b = await message.reply('<b>1) sᴇɴᴅ <code>/newbot</code> ᴛᴏ @BotFather\n2) ɢɪᴠᴇ ᴀ ɴᴀᴍᴇ ꜰᴏʀ ʏᴏᴜʀ ʙᴏᴛ.\n3) ɢɪᴠᴇ ᴀ ᴜɴɪǫᴜᴇ ᴜsᴇʀɴᴀᴍᴇ.\n4) ᴛʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏᴋᴇɴ.\n5) ꜰᴏʀᴡᴀʀᴅ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ ᴛᴏ ᴍᴇ.\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss.</b>')
        msg = await client.listen(message.from_user.id)
        if msg.text == '/cancel':
            await b.delete()
            return await message.reply('<b>ᴄᴀɴᴄᴇʟᴇᴅ ᴛʜɪs ᴘʀᴏᴄᴇss 🚫</b>')
        if msg.forward_from and msg.forward_from.id == 93372553:
            try:
                bot_token = re.findall(r"\b(\d+:[A-Za-z0-9_-]+)\b", msg.text)[0]
            except:
                await b.delete()
                return await message.reply('<b>sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ 😕</b>')
        else:
            await b.delete()
            return await message.reply('<b>ɴᴏᴛ ꜰᴏʀᴡᴀʀᴅᴇᴅ ꜰʀᴏᴍ @BotFather 😑</b>')
        await b.delete()
        token_found = await db.is_bot_found_using_token(bot_token)
        if token_found:
            return await message.reply("<b>⚠️ ᴏᴏᴘs! ᴛʜɪs ʙᴏᴛ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ...</b>")
        c = await message.reply('<b>🧑‍💻 ᴄʜᴇᴄᴋɪɴɢ ɪɴꜰᴏ...</b>')
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
        temp.CLONE_BOTS[message.from_user.id] = clone_bot
        await clone_bot.set_bot_commands(
            [BotCommand("start", "Start The Bot!"),
             BotCommand("stats", "Get Bot Status."),
             BotCommand("users", "Get Users."),
             BotCommand("broadcast", "Broadcast Message to bot users.")]
        )
        if message.from_user.username:
            owner = f"<a href=https://t.me/{message.from_user.username}>{message.from_user.first_name}</a>"
        else:
            owner = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
        await db.add_bot(message.from_user.id, owner, me.id, bot_token, me.username)
        tz = pytz.timezone('Asia/Colombo')
        await db.update_bot_last_used(me.id, datetime.now(tz))
        await client.send_message(LOG_CHANNEL, script.NEW_BOT_TXT.format(me.username, me.id, message.from_user.mention))
        await c.edit(f'<b>ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴ ʏᴏᴜʀ @{me.username} ʙᴏᴛ ɪs sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʀᴇᴀᴛᴇᴅ. ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ 🙂\n\nʏᴏᴜ ᴄᴀɴ ᴄᴜsᴛᴏᴍɪᴢᴇ ʏᴏᴜʀ ʙᴏᴛ ᴜsɪɴɢ /clone ᴄᴏᴍᴍᴀɴᴅ.</b>')
        await asyncio.sleep(0.2)
        await message.reply("<b>ᴀɴᴅ ᴅᴏɴ'ᴛ ꜰᴏʀɢᴇᴛ ᴛᴏ ᴀᴅᴅ ʟᴏɢ ᴄʜᴀɴɴᴇʟ 😐...\n\nᴡʜᴀᴛ ɪs ʟᴏɢ ᴄʜᴀɴɴᴇʟ?\n\nɪꜰ ᴀɴʏ ᴜsᴇʀ sᴛᴀʀᴛs ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ, ᴛʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ᴛʜᴇ ᴅᴀᴛᴀ ᴏꜰ ᴛʜᴀᴛ ᴜsᴇʀ ɪɴ ᴛʜᴇ ʟᴏɢ ᴄʜᴀɴɴᴇʟ. sᴇɴᴅ /clone ᴄᴏᴍᴍᴀɴᴅ ᴀɴᴅ ᴀᴅᴅ.</b>")
