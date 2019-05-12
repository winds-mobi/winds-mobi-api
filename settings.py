import os

SENTRY_DSN = os.environ.get('SENTRY_DSN')
ENVIRONMENT = os.environ.get('ENVIRONMENT') or 'development'

MONGODB_URL = os.environ.get('MONGODB_URL') or 'mongodb://localhost:27017/windmobile'

OPENAPI_PREFIX = os.environ.get('OPENAPI_PREFIX') or ''

try:
    from local_settings import *  # noqa
except ImportError:
    pass
