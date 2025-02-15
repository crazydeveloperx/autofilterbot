import motor.motor_asyncio
import os
import datetime

DATABASE_URI = os.getenv('DATABASE_URI', 'mongodb+srv://ClonedataAuto:ClonedataAuto@cluster0.tedkp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'Rajappan')

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return {
            'id': id,
            'name': name,
            '_id': int(id),
        }

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def delete_all_users(self):
        await self.col.delete_many({})

    async def update_user(self, user_data):
        await self.col.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)

    async def has_premium_access(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            expiry_time = user_data.get("expiry_time")
            if expiry_time is None:
                return False
            elif isinstance(expiry_time, datetime.datetime) and datetime.datetime.now() <= expiry_time:
                return True
            else:
                await self.col.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
        return False

    async def check_remaining_uasge(self, user_id):
        user_data = await self.get_user(user_id)
        expiry_time = user_data.get("expiry_time")
        remaining_time = expiry_time - datetime.datetime.now()
        return remaining_time

    async def remove_premium_access(self, user_id):
        return await self.col.update_one({"id": user_id}, {"$set": {"expiry_time": None}})

    async def get_user(self, user_id):
        user_data = await self.col.find_one({"id": user_id})
        return user_data

    async def get_database_size(self):
        return (await self.db.command("dbstats"))['dataSize']

ub = Database(DATABASE_URI, DATABASE_NAME)
