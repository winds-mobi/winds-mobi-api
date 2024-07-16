import asyncio
import logging
from contextlib import asynccontextmanager
from logging.config import dictConfig

import bson
import pymongo
import sentry_sdk
import uvloop
import yaml
from fastapi import FastAPI
from motor import motor_asyncio
from pymongo import MongoClient
from sentry_asgi import SentryMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from winds_mobi_api import database, views
from winds_mobi_api.settings import settings

with open(settings.log_config_path, "r") as file:
    dictConfig(yaml.load(file, Loader=yaml.FullLoader))
sentry_sdk.init(settings.sentry_dsn, environment=settings.environment)

log = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    database._mongodb = motor_asyncio.AsyncIOMotorClient(settings.mongodb_url).get_database()
    database._mongodb_sync = MongoClient(settings.mongodb_url).get_database()
    yield
    database.mongodb().client.close()
    database.mongodb_sync().client.close()


app = FastAPI(
    title="winds.mobi",
    version="2.3",
    lifespan=lifespan,
    root_path=settings.root_path,
    docs_url=f"/{settings.doc_path}",
    description="""### Feel free to "fair use" this API
Winds.mobi is a free, community [open source](https://github.com/winds-mobi) project. The data indexed by winds.mobi 
are kindly shared by their providers and belong to them.

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

Enjoy!

Yann
info@winds.mobi
""",  # noqa: W291
)
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_middleware(SentryMiddleware)


@app.exception_handler(pymongo.errors.OperationFailure)
async def mongodb_client_exception(request: Request, exc: pymongo.errors.OperationFailure):
    log.warning(f"Mongodb failure during request '{request.url}': {exc.details['errmsg']}")
    return JSONResponse({"detail": exc.details["errmsg"]}, status_code=400)


@app.exception_handler(pymongo.errors.PyMongoError)
@app.exception_handler(bson.errors.BSONError)
async def mongodb_server_exception(request: Request, exc: Exception):
    log.error(f"Mongodb error during request '{request.url}'", exc_info=exc)
    return JSONResponse({"detail": "Mongodb error"}, status_code=500)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url=settings.doc_path)


# Register our views
app.include_router(views.router, prefix="", tags=["Stations"])
