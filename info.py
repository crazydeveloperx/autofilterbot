import re
from os import environ

id_pattern = re.compile(r'^.\d+$')

# ------------------------------------------------------------------------ Bot information ---------------------------------------------------------------------------#

API_ID = int(environ.get('API_ID', '27499182'))
API_HASH = environ.get('API_HASH', '9c58142ef6abed28808a50e3e983c39c')
BOT_TOKEN = environ.get('BOT_TOKEN', '7009413270:AAEBPz1coKfT9MiTOS9IGhsUk5CMXgE1nKw')
BOT_USERNAME = environ.get('BOT_USERNAME', "Clonev3Bot")
PICS = (environ.get('PICS', 'https://telegra.ph/file/c60c61e9818ca1943c468.jpg')).split()
ADMINS = [int(admins) if id_pattern.search(admins) else admins for admins in environ.get('ADMINS', '6249148586').split()]

# ------------------------------------------------------------------------ Bot Index Channel ---------------------------------------------------------------------------#

INDEX_CHANNELS = [int(index_channels) if id_pattern.search(index_channels) else index_channels for index_channels in environ.get('INDEX_CHANNELS', '-1001956475641 -1004250021443').split()]

# ------------------------------------------------------------------------ Bot Public IndeX Group  ---------------------------------------------------------------------------#

PUBLICK_CHNL = int(environ.get('PUBLICK_CHNL', '-1004250021443'))

# ------------------------------------------------------------------------ Force channel and group  ---------------------------------------------------------------------------#

updates_channel = environ.get('UPDATES_CHANNEL', '-1001688312074')
UPDATES_CHANNEL = int(updates_channel) if updates_channel and id_pattern.search(updates_channel) else None
support_group = environ.get('SUPPORT_GROUP', '0')
SUPPORT_GROUP = int(support_group) if support_group and id_pattern.search(support_group) else None

# ------------------------------------------------------------------------ Log And Request channel  ---------------------------------------------------------------------------#

LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1001876507111'))
CLONE_REQ_CHANNEL = int(environ.get('CLONE_REQ_CHANNEL', '-1001915834318'))

# ------------------------------------------------------------------------ File Saver Database Url  ---------------------------------------------------------------------------#

DATABASE_URL = environ.get('DATABASE_URL', "mongodb+srv://FileSaveDb:FileSaveDb@cluster0.lsxuw8w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")

# ------------------------------------------------------------------------ Users And Autofilter Bot Saver Database Url  ---------------------------------------------------------------------------#

DB_URL = environ.get('DB_URL', "mongodb+srv://CloneDbM:CloneDbM@cluster0.ovb0cfy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = environ.get('DB_NAME', "Cluster0")

# ------------------------------------------------------------------------ Autofilter Bot Users Saver Database Url  ---------------------------------------------------------------------------#

CLONE_USER_DB_URL = environ.get('CLONE_USER_DB_URL', "mongodb+srv://CloneUsers:CloneUsers@cluster0.vidnkik.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
PREMIUM_DB_URL = environ.get('PREMIUM_DB_URL', "mongodb+srv://premiumusers:premiumusers@cluster0.drlvaai.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# ------------------------------------------------------------------------ Others  ---------------------------------------------------------------------------#

# button Links
UPDATES_CHANNEL_LINK = environ.get('UPDATES_CHANNEL_LINK', 'https://t.me/Crazybotz')
SUPPORT_GROUP_LINK = environ.get('SUPPORT_GROUP_LINK', 'https://t.me/Crazybotz')
MOVIE_GROUP_LINK = environ.get('MOVIE_GROUP_LINK', 'https://t.me/+v6h3boTBQXZlYWU1')

# Bot settings
MAX_BTN = int(environ.get('MAX_BTN', '8'))
DELETE_TIME = int(environ.get('DELETE_TIME', '1800'))
FILE_DELETE_TIME = int(environ.get('FILE_DELETE_TIME', '1800'))
PORT = environ.get("PORT", "8080")

# For clone bots

FILES_CHANNEL = environ.get('FILES_CHANNEL', 'clnfileschnl')
FILES_CHANNEL2 = environ.get('FILES_CHANNEL2', 'QuickXFiles')

F2LINK_C = environ.get("F2LINK_C", "-1001890815456")
ON_DWNLD = environ.get("ON_DWNLD", "aks-file-to-link-ashubhskeleton1.koyeb.app")
ON_WATCH = environ.get("ON_WATCH", "aks-file-to-link-ashubhskeleton1.koyeb.app")
