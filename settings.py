import os

SENTRY_URL = os.environ.get('SENTRY_URL') or ''
ENVIRONMENT = os.environ.get('ENVIRONMENT') or 'development'

MONGODB_URL = os.environ.get('MONGODB_URL') or 'mongodb://localhost:27017/windmobile'

try:
    from local_settings import *  # noqa
except ImportError:
    pass
