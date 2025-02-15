import logging
from pyrogram.errors import InputUserDeactivated, AccessTokenExpired, AccessTokenInvalid, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from info import UPDATES_CHANNEL, SUPPORT_GROUP, DELETE_TIME, MAX_BTN, API_ID, API_HASH, LOG_CHANNEL, DB_NAME, DB_URL
from imdb import Cinemagoer
import asyncio
from pyrogram.types import Message, InlineKeyboardButton, CallbackQuery, BotCommand
from pyrogram import Client, enums
from typing import Union
import re
import os
import base64
import time
from datetime import datetime
import pytz
from typing import List, Any
from database.db import db
from Script import script
from shortzy import Shortzy
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

SETTINGS = {}
imdb = Cinemagoer()

class temp(object):
    SEARCH = {}
    MOVIE_LIST = {}
    IMDB_TEMPLATE = {}
    INDEX_CANCEL = False
    BROADCAST_CANCEL = False
    BOT_USERNAME = None
    BOT_NAME = None
    BOT_ID = None
    BOT = None
    CRAZY = None
    BOT_START_TIME = 0
    CLONE_BOTS = {}
    CLONE_BOTS_START_TIME = {}


async def is_subscribed(bot, query):
    try:
        await bot.get_chat_member(UPDATES_CHANNEL, query.from_user.id)
        return True
    except UserNotParticipant:
        return False

async def is_joined(bot, query):
    try:
        await bot.get_chat_member(SUPPORT_GROUP, query.from_user.id)
        return True
    except UserNotParticipant:
        return False


async def get_settings(group_id):
    settings = SETTINGS.get(group_id)
    if not settings:
        settings = await db.get_settings(group_id)
        if settings is None:
            settings = {
                'imdb_poster': True,
                'imdb_template': script.IMDB_TEMPLATE,
                'auto_delete': False,
                'auto_delete_time': DELETE_TIME,
                'file_caption': script.FILE_CAPTION,
                'shortlink_url': "",
                'shortlink_api': "",
                'shortlink': False,
                'tutorial': "",
                'is_buttons': True
            }
        SETTINGS[group_id] = settings
    return settings

async def update_settings(group_id, type, value):
    current = await get_settings(group_id)
    current[type] = value
    SETTINGS[group_id] = current
    await db.update_settings(group_id, type, value)


async def get_poster(query, bulk=False, id=False, file=None, results=10):
    if not id:
        query = (query.strip()).lower()
        title = query
        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1]) 
        else:
            year = None
        movieid = imdb.search_movie(title.lower(), results=results)
        if not movieid:
            return None
        if year:
            filtered=list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if not filtered:
                filtered = movieid
        else:
            filtered = movieid
        movieid=list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if not movieid:
            movieid = filtered
        if bulk:
            return movieid
        movieid = movieid[0].movieID
    else:
        movieid = query
    movie = imdb.get_movie(movieid)
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    plot = movie.get('plot')
    if plot and len(plot) > 0:
        plot = plot[0]

    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."

    return {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer":list_to_str(movie.get("writer")),
        "producer":list_to_str(movie.get("producer")),
        "composer":list_to_str(movie.get("composer")) ,
        "cinematographer":list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url':f'https://www.imdb.com/title/tt{movieid}'
    }


async def users_broadcast(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except UserIsBlocked:
        return "Blocked"
    except Exception as e:
        await db.delete_user(user_id)
        await db.delete_user_admins(user_id)
        return "Failed"

async def groups_broadcast(group_id, message):
    try:
        m = await message.copy(chat_id=group_id)
        try:
            await m.pin()
        except:
            pass
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await groups_broadcast(group_id, message)
    except Exception as e:
        await db.delete_group(group_id)
        await db.delete_group_admins(group_id)
        return "Failed"


def get_size(size):
    """Get size in readable format"""

    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    else:
        return ' '.join(f'{elem}, ' for elem in k)


def get_time(seconds):
    """Get time in readable format"""

    result = ''
    days, remainder = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days} Days '
    hours, remainder = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours} Hours '
    minutes, seconds = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes} Minutes '
    seconds = int(seconds)
    if seconds != 0:
        result += f'{seconds} Seconds '
    if result == '':
        result += '🤷‍♂️'
    return result


async def get_shortlink(group_id, link):
    settings = await get_settings(group_id)
    url = settings['shortlink_url']
    api = settings['shortlink_api']
    shortzy = Shortzy(api_key=api, base_site=url)
    link = await shortzy.convert(link)
    return link

async def get_clone_bot_shortlink(bot_id, link):
    settings = await db.get_bot_settings(bot_id)
    url = settings['shortlink_url']
    api = settings['shortlink_api']
    shortzy = Shortzy(api_key=api, base_site=url)
    link = await shortzy.convert(link)
    return link


def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string


def get_status():
    tz = pytz.timezone('Asia/Colombo')
    hour = datetime.now(tz).time().hour
    if 5 <= hour < 12:
        sts = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ"
    elif 12 <= hour < 18:
        sts = "ɢᴏᴏᴅ ᴀꜰᴛᴇʀɴᴏᴏɴ"
    else:
        sts = "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ"
    return sts


async def is_clone_bot_force_subscribed(client, channel_id, user_id):
    try:
        await client.get_chat_member(channel_id, user_id)
        return True
    except UserNotParticipant:
        return False


async def add_new_group(client, message):
    if not await db.is_group_found(message.chat.id):
        await db.add_group(message.chat.id, message.chat.title)
        user = message.from_user.mention if message.from_user else "Anonymous"
        total = await client.get_chat_members_count(message.chat.id)
        username = f'@{message.chat.username}' if message.chat.username else 'Private'
        await client.send_message(LOG_CHANNEL, script.NEW_GROUP_TXT.format(message.chat.title, message.chat.id, username, total, user))
            
def get_media_from_message(message: "Message") -> Any:
    media_types = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return media


def get_hash(media_msg: Message) -> str:
    media = get_media_from_message(media_msg)
    return getattr(media, "file_unique_id", "")[:6]

async def au_restart_all_bots(query: CallbackQuery):
    await query.message.edit_text("Restarting all accepter bots...")
    bots = await db.get_all_bots()
    tasks = [restart_clone_bot(bot_info) for bot_info in bots]
    await asyncio.gather(*tasks)
    await query.message.edit_text("**All Autofilter Clone bots have been restarted.**")

async def restart_auclone_bot(bot):
    tz = pytz.timezone('Asia/Colombo')
    used = await db.get_bot_last_used(bot['bot_id'])
    last_used = datetime.now(tz) - used.astimezone(tz)
    
    if last_used.days >= 7:  # One Week
        await db.update_bot_settings(bot['bot_id'], 'is_active', False)
    
    settings = await db.get_bot_settings(bot['bot_id'])
    
    # Check if there's an existing bot instance and terminate it
    if bot['_id'] in temp.CLONE_BOTS:
        existing_bot = temp.CLONE_BOTS[bot['_id']]
        if existing_bot.is_connected:
            try:
                await existing_bot.stop()
            except Exception as e:
                print(f"Failed to stop the existing bot {bot['_id']}: {e}")
        del temp.CLONE_BOTS[bot['_id']]
    
    clone_bot = Client(
        name=bot['bot_token'],
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=bot['bot_token'],
        plugins={"root": "clone_plugins"}
    )
    temp.CLONE_BOTS[bot['_id']] = clone_bot
    
    try:
        await clone_bot.start()
        temp.CLONE_BOTS_START_TIME[bot['bot_id']] = time.time()
        me = await clone_bot.get_me()
        if settings['log_channel']:
            try:
                await clone_bot.send_message(settings['log_channel'], f"{me.mention} Restarted!")
            except Exception as e:
                print(f"Failed to send log message: {e}")
    except (AccessTokenExpired, AccessTokenInvalid) as e:
        print(f"Failed to start bot {bot['_id']}: {e}")
        await db.delete_bot(bot['_id'])

async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""
        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1
        unit = ts[index:]
        if value:
            value = int(value)
        return value, unit
    value, unit = extract_value_and_unit(time_string)
    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60
    elif unit == 'hour':
        return value * 3600
    elif unit == 'day':
        return value * 86400
    elif unit == 'month':
        return value * 86400 * 30
    elif unit == 'year':
        return value * 86400 * 365
    else:
        return 0

async def restart_clonkke_bot(bot):
    tz = pytz.timezone('Asia/Colombo')
    used = await db.get_bot_last_used(bot['bot_id'])
    last_used = datetime.now(tz) - used.astimezone(tz)
    
    if last_used.days >= 7:
        await db.update_bot_settings(bot['bot_id'], 'is_active', False)
    settings = await db.get_bot_settings(bot['bot_id'])
    clone_bot = Client(
        name=bot['bot_token'],
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=bot['bot_token'],
        plugins={"root": "clone_plugins"}
    )
    temp.CLONE_BOTS[bot['_id']] = clone_bot
    
    if settings['is_active']:
        try:
            await clone_bot.start()
            temp.CLONE_BOTS_START_TIME[bot['bot_id']] = time.time()
            
            await clone_bot.set_bot_commands([
                BotCommand("start", "Start The Bot!"),
                BotCommand("myplan", "Check Premium."),
                BotCommand("stats", "check bot status."),
                BotCommand("broadcast", "Broadcast Message to bot users.")
            ])
            
            me = await clone_bot.get_me()
            
            if settings['log_channel']:
                try:
                    await clone_bot.send_message(settings['log_channel'], f"{me.mention} Restarted!")
                except Exception as e:
                    print(f"Failed to send message to log channel: {e}")
        
        except (AccessTokenExpired, AccessTokenInvalid):
            await db.delete_bot(bot['_id'])


async def restart_clone_bot(bot):
    tz = pytz.timezone('Asia/Colombo')
    used = await db.get_bot_last_used(bot['bot_id'])
    last_used = datetime.now(tz) - used.astimezone(tz)
    if last_used.days >= 7:  # One Week
        await db.update_bot_settings(bot['bot_id'], 'is_active', False)
    settings = await db.get_bot_settings(bot['bot_id'])
    
    clone_bot = Client(
        name=bot['bot_token'],
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=bot['bot_token'],
        plugins={"root": "clone_plugins"}
    )
    temp.CLONE_BOTS[bot['_id']] = clone_bot
    if settings['is_active']:
        try:
            await clone_bot.start()
            temp.CLONE_BOTS_START_TIME[bot['bot_id']] = time.time()
            me = await clone_bot.get_me()
            admin = bot['_id']
            #await clone_bot.send_message(chat_id=admin, text=f"<b>✅ ʙᴏᴛ ʀᴇsᴛᴀʀᴛᴇᴅ</b>")
            print(f"{me.first_name} is started now ❤️")
            if settings['log_channel'] != "":
                try:
                    await clone_bot.send_message(settings['log_channel'], f"{me.mention} Restarted!")
                except:
                    pass
        except (AccessTokenExpired, AccessTokenInvalid):
            await db.delete_bot(bot['_id'])
