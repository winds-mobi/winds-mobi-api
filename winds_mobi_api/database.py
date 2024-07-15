from threading import local

from motor import motor_asyncio
from pymongo import MongoClient

from winds_mobi_api.settings import settings

motor_database = None
thread_local = local()


def mongodb():
    global motor_database
    if motor_database is None:
        motor_database = motor_asyncio.AsyncIOMotorClient(settings.mongodb_url).get_database()
    return motor_database


def mongodb_sync():
    if not hasattr(thread_local, "mongodb_database"):
        thread_local.mongodb_database = MongoClient(settings.mongodb_url).get_database()
    return thread_local.mongodb_database
