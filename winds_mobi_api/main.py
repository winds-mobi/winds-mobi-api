import asyncio
import logging.config
from os import path

import pymongo
import sentry_sdk
import uvloop
import yaml
from fastapi import FastAPI
from motor import motor_asyncio
from pymongo import MongoClient
from sentry_asgi import SentryMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, RedirectResponse

from settings import MONGODB_URL, SENTRY_DSN, ENVIRONMENT, OPENAPI_PREFIX, DOC_PATH
from winds_mobi_api import database, views

with open(path.join(path.dirname(path.abspath(__file__)), 'logging.yaml')) as f:
    logging.config.dictConfig(yaml.load(f, Loader=yaml.FullLoader))
sentry_sdk.init(SENTRY_DSN, environment=ENVIRONMENT)

log = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


app = FastAPI(
    title='winds.mobi',
    version='2.2',
    openapi_prefix=OPENAPI_PREFIX,
    docs_url=f'/{DOC_PATH}',
    description="""### Feel free to "fair use" this API
The data indexed by winds.mobi are kindly shared by their providers and belong to them.

1. Don't try to monetize your service that is using winds.mobi data in any way: paid application, subscription, 
in-app purchase, advertisement, ...

2. Don't overload this server by minimizing your number of calls:
- get data for multiple stations at once
- use cache in your backend application

3. Always publicly identify your calls to winds.mobi by doing at least one of the following:
- use an IP address with a `reverse DNS` (PTR record) to identify your backend application
- set an HTTP header `user-agent` to identify your backend application
- set an HTTP header `referer` (most browsers are doing it by default) to identify your web application

Any IP or application that doesn't respect these rules could be blacklisted without any notice.

Thanks!

Yann  
info@winds.mobi
"""
)
app.add_middleware(CORSMiddleware, allow_origins=['*'])
app.add_middleware(SentryMiddleware)


@app.on_event('startup')
async def startup_event():
    database._mongodb = motor_asyncio.AsyncIOMotorClient(MONGODB_URL).get_database()
    database._mongodb_sync = MongoClient(MONGODB_URL).get_database()


@app.exception_handler(pymongo.errors.OperationFailure)
async def mongo_exception(request, exc):
    log.error('Mongodb error', exc_info=exc)
    return JSONResponse({'detail': 'Mongodb error'}, status_code=400)


@app.get('/', include_in_schema=False)
async def root():
    return RedirectResponse(url=DOC_PATH)

# Register our views
app.include_router(views.router, prefix='', tags=['Stations'])
