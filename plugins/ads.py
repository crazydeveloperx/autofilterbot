import pymongo
from pyrogram import Client, filters, enums

DB_URL = 'mongodb+srv://ClonedataAuto:ClonedataAuto@cluster0.tedkp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
DB_NAME = 'Rajappan'

dbclient = pymongo.MongoClient(DB_URL)
database = dbclient[DB_NAME]
footer_text = database['footer_text']

async def set_footer_text(footer: str):
    footer_text.update_one(
        {'_id': 'footer_content'},
        {'$set': {'text': footer}},
        upsert=True
    )

async def get_footer_text():
    config = footer_text.find_one({'_id': 'footer_content'})
    if config:
        return config.get('text', "")
    return ""


async def delete_footer_text():
    result = footer_text.delete_one({'_id': 'footer_content'})
    return result.deleted_count > 0
