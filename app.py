import asyncio
import logging.config
from os import path

import pymongo
import sentry_sdk
import uvloop
import yaml
from fastapi import FastAPI
from motor import motor_asyncio
from sentry_asgi import SentryMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from settings import MONGODB_URL, SENTRY_DSN, ENVIRONMENT, OPENAPI_PREFIX

with open(path.join(path.dirname(path.abspath(__file__)), 'logging.yaml')) as f:
    logging.config.dictConfig(yaml.load(f))
sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT)

log = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
mongo_db = None


def get_mongo_db():
    global mongo_db

    if not mongo_db:
        mongo_db = motor_asyncio.AsyncIOMotorClient(MONGODB_URL).get_database()
    return mongo_db


app = FastAPI(
    title='winds.mobi',
    version='2.1',
    openapi_prefix=OPENAPI_PREFIX,
    docs_url='/doc'
)
app.add_middleware(CORSMiddleware, allow_origins=['*'])
app.add_middleware(SentryMiddleware)


@app.exception_handler(pymongo.errors.OperationFailure)
async def mongo_exception(request, exc):
    log.error('Mongodb error', exc_info=exc)
    return JSONResponse({'detail': 'Mongodb error'}, status_code=400)

# Register our views
import winds_mobi_api.views  # noqa
