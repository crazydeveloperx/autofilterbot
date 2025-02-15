from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest
from database.db import db
from clone_database.users_db import find_join_req, add_join_req, del_join_req

@Client.on_chat_join_request()
async def join_reqs(client, message: ChatJoinRequest):
    me = await client.get_me()
    settings = await db.get_bot_settings(me.id)
    if message.chat.id == settings['force_channel']:
        if not await find_join_req(me.id, settings['force_channel'], message.from_user.id):
            await add_join_req(me.id, settings['force_channel'], message.from_user.id)

@Client.on_message(filters.command("delreq"))
async def delreq_handler(client, message):
    me = await client.get_me()
    bot = await db.get_bot(me.id)
    settings = await db.get_bot_settings(me.id)
    
    if bot['_id'] != message.from_user.id:
        return await message.reply('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪs ʙᴏᴛ 😑</b>')
    
    await del_join_req(me.id, settings['force_channel'])
    await message.reply("<b>⚙ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ</b>")
