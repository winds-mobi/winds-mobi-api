import asyncio
import logging
from logging.config import dictConfig

import bson
import pymongo
import sentry_sdk
import uvloop
import yaml
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from winds_mobi_api import views
from winds_mobi_api.settings import settings

with open(settings.log_config_path) as file:
    dictConfig(yaml.load(file, Loader=yaml.FullLoader))
sentry_sdk.init(settings.sentry_url, environment=settings.environment)

log = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(
    title="winds.mobi",
    version="2.3",
    root_path=settings.root_path,
    docs_url=f"/{settings.doc_path}",
    description="""### Feel free to "fair use" this API
Winds.mobi is a free, community-driven, [open source](https://github.com/winds-mobi) project. The data indexed by 
winds.mobi are kindly shared by their providers and belong to them.

Terms of Use:
1. Always identify your calls to winds.mobi API by setting a **user-agent HTTP header** containing a string that 
identifies you, for example, `user-agent: my-service.cloud`.

2. **Do not monetize** your service using winds.mobi data in any way: paid application, subscription, 
in-app purchase, advertisement, ...

3. **Do not overload** this server by minimizing your number of calls. Get data for multiple stations at once.

Any IP or service that doesn't respect these rules will be blacklisted without any notice.

Enjoy!

Yann  
info@winds.mobi
""",  # noqa: W291
)
app.add_middleware(CORSMiddleware, allow_origins=["*"])


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
