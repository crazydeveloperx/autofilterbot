from info import DB_NAME, DB_URL, MAX_BTN, DELETE_TIME, FILE_DELETE_TIME
from Script import script
from pymongo import MongoClient

myclient = MongoClient(DB_URL)
mydb = myclient[DB_NAME]
usrcol = mydb['users']
botcol = mydb['Bots']
grpcol = mydb['groups']
admcol = mydb['Admins']

class Database:
    async def add_user(self, id, name):
        user = {'id': id, 'name': name}
        usrcol.insert_one(user)

    async def add_group(self, id, title):
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
        group = {'_id': id, 'title': title, 'settings': settings}
        grpcol.insert_one(group)

    async def update_settings(self, id, type, value):
        grpcol.update_one({'_id': id}, {'$set': {f'settings.{type}': value}})

    async def get_settings(self, id):
        group = grpcol.find_one({'_id': id})
        if not group:
            return None
        return group.get('settings')

    async def is_group_found(self, id):
        group = grpcol.find_one({'_id': id})
        return bool(group)

    async def add_bot(self, user_id, owner, bot_id, bot_token, username):
        settings = {
            'is_active': True,
            'imdb_poster': True,
            'imdb_template': script.IMDB_TEMPLATE,
            'auto_delete': False,
            'auto_delete_time': DELETE_TIME,
            'file_auto_delete': False,
            'file_auto_delete_time': FILE_DELETE_TIME,
            'file_caption': script.FILE_CAPTION,
            'shortlink_url': "",
            'shortlink_api': "",
            'shortlink': False,
            'tutorial': "",
            'group_link': "",
            'max_results': MAX_BTN,
            'start_text': "<b>Hey {mention},\n\nI'm Autofilter Bot, I will give any movie or series in your group. Just add me your group as admin.\n\nTo know more click help button.</b>",
            'start_pic': "",
            'welcome_user': False,
            'welcome_text': "<b>ʜᴇʏ, ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ.</b>",
            'welcome_pic': "",
            'premium_mode': True,
            'premium_text': "<b>👋 Hey There,\n\n<u>- ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴs -</u>\n\n- 30ʀs - 1 ᴡᴇᴇᴋ\n- 50ʀs - 1 ᴍᴏɴᴛʜs\n- 120ʀs - 3 ᴍᴏɴᴛʜs\n- 220ʀs - 6 ᴍᴏɴᴛʜs\n\n<u>Pʀᴇᴍɪᴜᴍ Fᴇᴀᴛᴜʀᴇs 🎁</u>\n\n○ ᴅɪʀᴇᴄᴛ ғɪʟᴇs\n○ ᴀᴅ-ғʀᴇᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ\n○ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs & sᴇʀɪᴇs\n•────•────────•────•\n\n✨ ᴜᴘɪ ɪᴅ - <code>9531506491@ibl</code>\n➥ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ /myplan\n\n💢 ᴍᴜsᴛ sᴇɴᴅ sᴄʀᴇᴇɴsʜᴏᴛ ᴀғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ.‼️\nᴀғᴛᴇʀ sᴇɴᴅɪɴɢ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ᴘʟᴇᴀsᴇ ɢɪᴠᴇ ᴜs sᴏᴍᴇ ᴛɪᴍᴇ ᴛᴏ ᴀᴅᴅ ʏᴏᴜ ɪɴ ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ ʟɪsᴛ.</b>",
            
            'file_button_url': "",
            'file_button_text': "",
            'button_url': "",
            'button_text': "",
            'sec_button_url': "",
            'sec_button_text': "",
            
            'force_channel': "",
            'force_subscribe': False,
            'req_fsub': False,
            'mongodb': "",
            'log_channel': "",
            'clone_admin': "",
            'is_verify': False,
            'verify_time_1': 21600,
            'clone_buttons': True,
            'pm_search': False,
            'spell_check': True,
            'telegraph_mode': False,
            'admin_ids': [],
            'last_used': ""
        }
        bot = {'_id': user_id, 'owner': owner, 'bot_token': bot_token, 'bot_id': bot_id, 'username': username, 'settings': settings}
        botcol.insert_one(bot)

    async def get_bot_from_user(self, id):
        bot = botcol.find_one({'_id': id})
        return bot

    async def get_bot(self, id):
        bot = botcol.find_one({'bot_id': id})
        return bot

    async def get_bot_last_used(self, id):
        bot = botcol.find_one({'bot_id': id})
        return bot.get('last_used')

    async def update_bot_last_used(self, id, date):
        botcol.update_one({'bot_id': id}, {'$set': {'last_used': date}})

    async def get_bot_settings(self, id):
        bot = botcol.find_one({'bot_id': id})
        return bot.get('settings')

    async def update_bot_settings(self, id, type, value):
        botcol.update_one({'bot_id': id}, {'$set': {f'settings.{type}': value}})

    async def is_bot_found_using_user(self, user_id):
        bot = botcol.find_one({'_id': user_id})
        return bool(bot)

    async def is_bot_found_using_token(self, token):
        bot = botcol.find_one({'bot_token': token})
        return bool(bot)

    async def is_user_found(self, id):
        user = usrcol.find_one({'id': id})
        return bool(user)

    async def total_users_count(self):
        count = usrcol.count_documents({})
        return count

    async def total_bots_count(self):
        count = botcol.count_documents({})
        return count

    async def total_active_bots_count(self):
        count = botcol.count_documents({'settings.is_active': True})
        return count
    
    async def total_inactive_bots_count(self):
        count = botcol.count_documents({'settings.is_active': False})
        return count

    async def total_groups_count(self):
        count = grpcol.count_documents({})
        return count

    async def delete_user(self, user_id):
        usrcol.delete_one({'id': user_id})

    async def delete_bot(self, user_id):
        botcol.delete_one({'_id': user_id})

    async def delete_all_bots(self):
        try:
            botcol.delete_many({})
            return True
        except Exception as e:
            print(f"Error deleting clones: {e}")
            return False

    async def delete_group(self, id):
        grpcol.delete_one({'_id': id})

    async def get_all_groups(self):
        return grpcol.find()

    async def get_all_users(self):
        return usrcol.find()

    async def get_all_bots(self):
        return botcol.find()

    async def get_admin_groups(self, user_id):
        user = admcol.find_one({'_id': user_id})
        if user:
            return user["groups"]
        else:
            return []

    async def add_admin_group(self, user_id, group_id):
        user = admcol.find_one({'_id': user_id})
        if user:
            if group_id not in user["groups"]:
                admcol.update_one({'_id': user_id}, {"$push": {"groups": group_id}})
        else:
            admcol.insert_one({'_id': user_id, 'groups': [group_id]})

    async def delete_admin_group(self, user_id, group_id):
        admcol.update_one({"_id": user_id}, {"$pull": {"groups": group_id}})

    async def delete_user_admins(self, user_id):
        admcol.delete_one({'_id': user_id})

    async def delete_group_admins(self, group_id):
        admcol.update_many({"groups": group_id}, {"$pull": {"groups": group_id}})

    async def get_db_size(self):
        size = mydb.command("dbstats")['dataSize']
        return size


db = Database()
