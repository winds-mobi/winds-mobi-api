from motor import motor_asyncio

from winds_mobi_api.settings import settings

motor_database = None


def mongodb():
    global motor_database
    if motor_database is None:
        motor_database = motor_asyncio.AsyncIOMotorClient(settings.mongodb_url).get_database()
    return motor_database
