import os
from datetime import timedelta
import structlog
import sefaria.system.logging as sefaria_logging

# MongoDB settings
SEFARIA_DB = os.getenv('MONGO_URL', 'mongodb://localhost:27017/sefaria')
SEFARIA_DB_USER = os.getenv('MONGO_DB_USER', '')
SEFARIA_DB_PASSWORD = os.getenv('MONGO_DB_PASSWORD', '')

# PostgreSQL settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'sefaria_auth'),
        'USER': os.getenv('POSTGRES_USER', 'admin'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'admin'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Security and hosting
SECRET_KEY = os.getenv('SECRET_KEY', 'insert your long random secret key here !')
ALLOWED_HOSTS = ['*']
DEBUG = False

# Admin settings
ADMINS = (
    ('Your Name', 'you@example.com'),
)
ADMIN_PATH = 'admin'

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'shared': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
SESSION_CACHE_ALIAS = 'default'
USER_AGENTS_CACHE = 'default'
SHARED_DATA_CACHE_ALIAS = 'shared'

# Site settings
SITE_PACKAGE = 'sites.sefaria'
DOMAIN_LANGUAGES = {}

# Email settings
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Search settings
SEARCH_URL = 'http://localhost:9200'
SEARCH_INDEX_ON_SAVE = False
SEARCH_INDEX_NAME_TEXT = 'text'
SEARCH_INDEX_NAME_SHEET = 'sheet'

# Node settings
USE_NODE = False
NODE_HOST = 'http://localhost:4040'
NODE_TIMEOUT = 10

# CRM settings
CRM_TYPE = 'NONE'
NATIONBUILDER_SLUG = ""
NATIONBUILDER_TOKEN = ""
NATIONBUILDER_CLIENT_ID = ""
NATIONBUILDER_CLIENT_SECRET = ""

# Varnish settings
USE_VARNISH = False
FRONT_END_URL = 'http://localhost:8000'
VARNISH_ADM_ADDR = 'localhost:6082'
VARNISH_HOST = 'localhost'
VARNISH_FRNT_PORT = 8040
VARNISH_SECRET = '/etc/varnish/secret'
USE_VARNISH_ESI = False

# Other settings
DISABLE_INDEX_SAVE = False
DISABLE_AUTOCOMPLETER = False
ENABLE_LINKER = False
MULTISERVER_ENABLED = False
SEFARIA_DATA_PATH = '/path/to/your/Sefaria-Data'
SEFARIA_EXPORT_PATH = '/path/to/your/Sefaria-Data/export'
GOOGLE_GTAG = ''
GOOGLE_TAG_MANAGER_CODE = ''
HOTJAR_ID = None

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': True,
    'SIGNING_KEY': 'a signing key: at least 256 bits',
}

# Celery settings
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1')
REDIS_PORT = 6379
REDIS_PASSWORD = None
CELERY_REDIS_BROKER_DB_NUM = 2
CELERY_REDIS_RESULT_BACKEND_DB_NUM = 3
CELERY_QUEUES = {}
CELERY_ENABLED = False

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json_formatter': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.processors.JSONRenderer(),
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'json_formatter',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'propagate': False,
        },
        'django': {
            'handlers': ['default'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['default'],
            'propagate': False,
        },
    }
}

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.stdlib.add_logger_name,
        sefaria_logging.add_severity,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        sefaria_logging.log_exception_info,
        structlog.processors.UnicodeDecoder(),
        sefaria_logging.decompose_request_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Webhook settings
WEBHOOK_USERNAME = os.getenv('WEBHOOK_USERNAME')
WEBHOOK_PASSWORD = os.getenv('WEBHOOK_PASSWORD')
