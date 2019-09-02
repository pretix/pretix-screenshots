import atexit
import os
import tempfile

tmpdir = tempfile.TemporaryDirectory()
os.environ.setdefault('DATA_DIR', tmpdir.name)
if os.path.exists('test/sqlite.cfg'):
    os.environ.setdefault('PRETIX_CONFIG_FILE', 'test/sqlite.cfg')

from pretix.settings import *  # NOQA

DATA_DIR = tmpdir.name
LOG_DIR = os.path.join(DATA_DIR, 'logs')
MEDIA_ROOT = os.path.join(DATA_DIR, 'media')
SITE_URL = "http://example.com"

LOCALE_PATHS = list(LOCALE_PATHS) + [
    os.path.join(os.path.dirname(__file__), 'locale'),
]

atexit.register(tmpdir.cleanup)

EMAIL_BACKEND = 'django.core.mail.outbox'

COMPRESS_ENABLED = COMPRESS_OFFLINE = False
COMPRESS_CACHE_BACKEND = 'testcache'
#STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
PRETIX_INSTANCE_NAME = 'pretix.eu'

# Disable celery
CELERY_ALWAYS_EAGER = True
HAS_CELERY = False
CELERY_BROKER_URL = None
CELERY_RESULT_BACKEND = None
CELERY_TASK_ALWAYS_EAGER = True

# Don't use redis
SESSION_ENGINE = "django.contrib.sessions.backends.db"
HAS_REDIS = False
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

try:
    import pretixeu

    TEMPLATES[0]['DIRS'].insert(0, os.path.join(os.path.dirname(pretixeu.__file__), 'templates'))
    TEMPLATES[0]['OPTIONS']['context_processors'].append('pretixeu.billing.context.contextprocessor')
except ImportError:
    pass


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()
