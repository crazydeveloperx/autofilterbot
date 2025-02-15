from pyrogram import Client, filters
from database.db import db
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

@Client.on_message(filters.new_chat_members & filters.group)
async def welcome_message(client, message):
    me = await client.get_me()
    settings = await db.get_bot_settings(me.id)
    if settings.get('welcome_user'):
        for member in message.new_chat_members:
            welcome_text_template = settings.get('welcome_text', '')
            welcome_text = welcome_text_template.format(
                mention=member.mention,
                chat_title=message.chat.title
            )
            inline_buttons = []
            if settings.get('update'):
                inline_buttons.append([
                    InlineKeyboardButton('🍁 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 🍁', url=settings['update'])
                ])
            reply_markup = InlineKeyboardMarkup(inline_buttons) if inline_buttons else None
            if not settings.get('welcome_pic'):
                await message.reply_text(welcome_text, reply_markup=reply_markup)
            else:
                await message.reply_photo(photo=settings['welcome_pic'], caption=welcome_text, reply_markup=reply_markup)
