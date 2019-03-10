LOG_DIR = None
SENTRY_URL = ''

MONGODB_URL = 'mongodb://localhost:27017/windmobile'

try:
    from local_settings import *  # noqa
except ImportError:
    pass
