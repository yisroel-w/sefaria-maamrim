import os

# MongoDB settings
SEFARIA_DB = os.getenv('MONGO_URL', 'mongodb://localhost:27017/sefaria')
SEFARIA_DB_USER = os.getenv('SEFARIA_DB_USER', '')
SEFARIA_DB_PASSWORD = os.getenv('SEFARIA_DB_PASSWORD', '')

# Redis settings
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# Database settings (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'sefaria_auth'),
        'USER': os.getenv('POSTGRES_USER', 'admin'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'admin'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': 0,
    }
}

# Security settings
SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key-please-change')
ALLOWED_HOSTS = ['*']
DEBUG = False

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': REDIS_URL,
        'TIMEOUT': None,
    }
}

# Site settings
SITE_PACKAGE = 'reader'
SITE_SETTINGS = {
    'TOR2WEB': False,
    'MAINTENANCE_MESSAGE': '',
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

# JWT settings
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'USER_ID_FIELD': 'email',
    'USER_ID_CLAIM': 'email',
}

# CRM settings
CRM_TYPE = "NONE"
NATIONBUILDER_SLUG = ""
NATIONBUILDER_TOKEN = ""
NATIONBUILDER_CLIENT_ID = ""
NATIONBUILDER_CLIENT_SECRET = ""

# Reference model settings
RAW_REF_MODEL_BY_LANG_FILEPATH = os.getenv('RAW_REF_MODEL_BY_LANG_FILEPATH', None)
RAW_REF_PART_MODEL_BY_LANG_FILEPATH = os.getenv('RAW_REF_PART_MODEL_BY_LANG_FILEPATH', None)

# Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Structlog settings
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
