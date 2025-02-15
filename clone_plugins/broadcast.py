from pyrogram import Client, filters
import datetime
import time
from database.db import db
from info import ADMINS
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, MessageIdInvalid, ChatWriteForbidden
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import get_time
from pymongo import MongoClient
import asyncio
from clone_database.users_db import get_clone_bot_all_users, get_clone_bot_users_count, delete_clone_bot_user

class broadcast_temp(object):
    IS_BROADCASTINGS = {}
    IS_CANCELS = {}

@Client.on_callback_query(filters.regex(r'^broadcast_cancel'))
async def broadcast_cancel(bot, query):
    await query.message.edit("Trying to cancel your broadcasting...")
    broadcast_temp.IS_CANCELS[query.from_user.id] = True

@Client.on_message(filters.private & filters.command("broadcast"))
async def broadcast(client, message):
    me = await client.get_me()
    bot = await db.get_bot(me.id)
    settings = await db.get_bot_settings(me.id)
    admin_ids = settings.get("admin_ids", [])
    if bot['_id'] != message.from_user.id and message.from_user.id not in admin_ids:
        return

    if broadcast_temp.IS_BROADCASTINGS.get(message.from_user.id):
        return await message.reply('<b>Broadcast process already running, please wait for it to complete.</b>')

    if not message.reply_to_message:
        return await message.reply('<b>Reply to any message to broadcast.</b>')

    msg = await message.reply_text('<b>Broadcasting your message...</b>')
    broadcast_msg = message.reply_to_message
    users = await get_clone_bot_all_users(me.id)
    total_users = await get_clone_bot_users_count(me.id)
    
    broadcast_temp.IS_BROADCASTINGS[message.from_user.id] = True
    broadcast_temp.IS_CANCELS[message.from_user.id] = False
    
    done = 0
    blocked = 0
    failed = 0
    success = 0
    start_time = time.time()

    for user in users:
        if broadcast_temp.IS_CANCELS.get(message.from_user.id):
            break

        status = await broadcast_clone_bot(me.id, user['_id'], broadcast_msg)
        if status == "Success":
            success += 1
        elif status == "Blocked":
            blocked += 1
        elif status == "Failed":
            failed += 1

        done += 1
        if done % 10 == 0:
            btn = [[
                InlineKeyboardButton('Cancel', callback_data=f'broadcast_cancel')
            ]]
            try:
                await msg.edit(f"<b>Broadcast processing...\n\nTotal users - <code>{total_users}</code>\nCompleted - <code>{done} / {total_users}</code>\nSuccess - <code>{success}</code>\nBlocked - <code>{blocked}</code>\nFailed - <code>{failed}</code></b>", reply_markup=InlineKeyboardMarkup(btn))
            except (FloodWait, MessageNotModified, MessageIdInvalid, ChatWriteForbidden) as e:
                if isinstance(e, FloodWait):
                    await asyncio.sleep(e.value)
                else:
                    print(f"Failed to edit message: {e}")

    time_taken = get_time(time.time() - start_time)
    broadcast_temp.IS_BROADCASTINGS[message.from_user.id] = False
    await msg.edit(f"<b>Broadcast completed\n\nTime taken - <code>{time_taken}</code>\nTotal users - <code>{total_users}</code>\nCompleted - <code>{done} / {total_users}</code>\nSuccess - <code>{success}</code>\nBlocked - <code>{blocked}</code>\nFailed - <code>{failed}</code></b>")

async def broadcast_clone_bot(bot_id, user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_clone_bot(bot_id, user_id, message)
    except UserIsBlocked:
        return "Blocked"
    except Exception as e:
        await delete_clone_bot_user(bot_id, user_id)
        return "Failed"
