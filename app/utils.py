import os
from uuid import uuid4

import motor.motor_asyncio

mongo_host = os.environ.get('MONGO_DB_HOST', 'mongodb://root:example@localhost:27017/')
client = motor.motor_asyncio.AsyncIOMotorClient(mongo_host)
db = client.link_shortener_db


async def add_short_link(long_url: str, short_url: str = None, user_id=None):
    isShortExists = await db.links.find_one({"short_url": short_url})
    if short_url and isShortExists:
        return None
    if not short_url:
        short_url = str(uuid4())
    if user_id:
        data = {
            "long_url": long_url,
            "short_url": short_url,
            "user_id": user_id
        }
    else:
        data = {
            "long_url": long_url,
            "short_url": short_url
        }
    await db.links.insert_one(data)
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


async def add_user(user_data):
    isUser = await db.users.find_one({"user_id": user_data.id})
    if not isUser:
        user_dict = {
            'user_id': user_data.id,
            'first_name': user_data.first_name,
            'last_name': user_data.last_name,
            'username': user_data.username,
            'language_code': user_data.language_code
        }
        await db.users.insert_one(user_dict)


# async def get_all_user_links(user_id): TODO
#     all_links_data = db.links.find({"user_id": user_id})
#     results = []
#     async for link in all_links_data:
#         results.append(link)
#     return results


async def add_redirect(short_url):
    url_data = await db.links.find_one({"short_url": short_url})
    if url_data and url_data.get('user_id'):
        await db.redirects.insert_one({
            'short_url': short_url,
            'owner': url_data['user_id']
        })
    else:
        print("error")
