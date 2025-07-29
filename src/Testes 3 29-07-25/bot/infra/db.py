from motor.motor_asyncio import AsyncIOMotorClient  # driver async do Mongo
from os import getenv

MONGO_URI = getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = getenv("MONGO_DBNAME", "Projeto")

_client = AsyncIOMotorClient(MONGO_URI)
db      = _client[DB_NAME]

async def insert_one(coll: str, doc: dict):
    return (await db[coll].insert_one(doc)).inserted_id

async def delete_one(coll: str, filt: dict):
    return await db[coll].delete_one(filt)

async def find_one_and_delete(coll: str, filt: dict):
    return await db[coll].find_one_and_delete(filt)
