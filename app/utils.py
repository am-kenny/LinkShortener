import os
from uuid import uuid4

import motor.motor_asyncio

mongo_host = os.environ.get('MONGO_DB_HOST', 'mongodb://root:example@localhost:27017/')
client = motor.motor_asyncio.AsyncIOMotorClient(mongo_host)
db = client.link_shortener_db


async def add_short_link(long_url: str, short_url: str):
    isShortExists = await db.links.find_one({"short_url": short_url})
    if short_url and isShortExists:
        return None
    if not short_url:
        short_url = str(uuid4())
    await db.links.insert_one({"long_url": long_url, "short_url": short_url})
    return short_url


async def get_long_link(short_url: str):
    url_data = await db.links.find_one({"short_url": short_url})
    if url_data:
        return url_data["long_url"]
    else:
        return None


async def update_short_link(short_url: str, new_long_url: str):
    original_long_url = await db.links.find_one({"short_url": short_url})
    if original_long_url:
        new_long_url = {"long_url": new_long_url}
        await db.links.update_one({"_id": original_long_url["_id"]}, {"$set": new_long_url})
        return short_url
    else:
        return None


