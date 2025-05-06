# local_settings.py tailored for Render deployment
import os
from datetime import timedelta
import structlog
# Assuming sefaria.system.logging exists relative to the project root
# from sefaria.system import logging as sefaria_logging # Uncomment if you encounter import issues with the original line
# If the above doesn't work, you might need to adjust the import path based on your project structure
# Or, if this import itself causes issues, temporarily comment out logging configurations that rely on it
import logging # Standard library logging import
import sys # Needed for sys.stdout in logging
import django.utils.log # Needed for Django's logging filters

# --- General Settings ---
DEBUG = False # Should be False for production on Render
ALLOWED_HOSTS = ['*'] # Allows access from any host, necessary for Render's dynamic IPs

# --- Database Settings (PostgreSQL for Auth, MongoDB for Sefaria Data) ---
# PostgreSQL for Django's auth and other relational data
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'sefaria_auth'), # Reads from Render Environment Variable POSTGRES_DB
        'USER': os.getenv('POSTGRES_USER', 'admin'),    # Reads from Render Environment Variable POSTGRES_USER
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'admin'), # Reads from Render Environment Variable POSTGRES_PASSWORD
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'), # Reads from Render Environment Variable POSTGRES_HOST
        'PORT': os.getenv('POSTGRES_PORT', '5432'),    # Reads from Render Environment Variable POSTGRES_PORT
    }
}

# MongoDB for Sefaria's primary data
# Use MONGO_URL environment variable for connection string
# Fallback to localhost:27017/sefaria for local development if MONGO_URL is not set
SEFARIA_DB = os.getenv('MONGO_URL', 'mongodb://localhost:27017/sefaria') # Reads from Render Environment Variable MONGO_URL
SEFARIA_DB_USER = os.getenv('MONGO_DB_USER', '') # Optional: Reads from Render Environment Variable MONGO_DB_USER
SEFARIA_DB_PASSWORD = os.getenv('MONGO_DB_PASSWORD', '') # Optional: Reads from Render Environment Variable MONGO_DB_PASSWORD

# Required by sefaria.system.database for replica set configuration check
# Set to None if not using a replica set (typical for free Atlas clusters)
MONGO_REPLICASET_NAME = None

# --- Security Settings ---
SECRET_KEY = os.getenv('SECRET_KEY', 'insert your long random secret key here !') # Reads from Render Environment Variable SECRET_KEY

# --- Admin settings ---
ADMINS = (
    ('Your Name', 'you@example.com'), # Update with your info
)
ADMIN_PATH = 'admin' # This will be the path to the admin site

# --- Cache settings (Using Redis via REDIS_URL environment variable) ---
# Fallback to DummyCache for local development if REDIS_URL is not set
# You'll need django-redis installed (should be in requirements.txt)
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0') # Reads from Render Environment Variable REDIS_URL

CACHES = {
    "shared": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "SERIALIZER": "django_redis.serializers.json.JSONSerializer", # This is the default, we override it to ensure_ascii=False if needed later
            # Ensure your Redis URL includes the password if authentication is enabled
        },
        "TIMEOUT": None, # Cache items do not expire by default
    },
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
             # "SERIALIZER": "django_redis.serializers.json.JSONSerializer", # This is the default
        },
        "TIMEOUT": 60 * 60 * 24 * 30, # Default cache timeout: 30 days
    },
}

SESSION_CACHE_ALIAS = "default"
USER_AGENTS_CACHE = 'default' # If using django-user-agents and cache
SHARED_DATA_CACHE_ALIAS = 'shared'


# --- Site settings ---
SITE_PACKAGE = 'sites.sefaria' # Keep this as is
DOMAIN_LANGUAGES = {} # Keep this as is unless you have specific domain language needs


# --- Email settings ---
# Configure these if you want mail_admins handler to work
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost') # Reads from Render Environment Variable EMAIL_HOST (optional)
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 1025)) # Reads from Render Environment Variable EMAIL_PORT (optional)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend') # Reads from Render Environment Variable EMAIL_BACKEND (optional)


# --- Search settings ---
SEARCH_URL = os.getenv('SEARCH_URL', 'http://localhost:9200') # Reads from Render Environment Variable SEARCH_URL (optional)
SEARCH_INDEX_ON_SAVE = False
SEARCH_INDEX_NAME_TEXT = 'text'
SEARCH_INDEX_NAME_SHEET = 'sheet'

# --- Node settings (Likely not needed for basic deployment) ---
USE_NODE = False
NODE_HOST = "http://localhost:4040"
NODE_TIMEOUT = 10

# --- CRM settings ---
# Define CRM settings even if not used to prevent AttributeErrors
CRM_TYPE = os.getenv('CRM_TYPE', 'NONE') # Reads from Render Environment Variable CRM_TYPE (optional, defaults to 'NONE')

NATIONBUILDER_SLUG = os.getenv('NATIONBUILDER_SLUG', '') # Defined to prevent AttributeError
NATIONBUILDER_TOKEN = os.getenv('NATIONBUILDER_TOKEN', '')
NATIONBUILDER_CLIENT_ID = os.getenv('NATIONBUILDER_CLIENT_ID', '')
NATIONBUILDER_CLIENT_SECRET = os.getenv('NATIONBUILDER_CLIENT_SECRET', '')

SALESFORCE_BASE_URL = os.getenv('SALESFORCE_BASE_URL', '') # Defined to prevent AttributeError
SALESFORCE_CLIENT_ID = os.getenv('SALESFORCE_CLIENT_ID', '')
SALESFORCE_CLIENT_SECRET = os.getenv('SALESFORCE_CLIENT_SECRET', '')


# --- Varnish settings (Likely not needed for basic deployment) ---
USE_VARNISH = False
FRONT_END_URL = os.getenv('FRONT_END_URL', 'http://localhost:8000')
VARNISH_ADM_ADDR = os.getenv('VARNISH_ADM_ADDR', 'localhost:6082')
VARNISH_HOST = os.getenv('VARNISH_HOST', 'localhost')
VARNISH_FRNT_PORT = int(os.getenv('VARNISH_FRNT_PORT', 8040))
VARNISH_SECRET = os.getenv('VARNISH_SECRET', '/etc/varnish/secret')
USE_VARNISH_ESI = False

# --- Other settings ---
DISABLE_INDEX_SAVE = False
DISABLE_AUTOCOMPLETER = False
ENABLE_LINKER = False # Set to True if you want to enable the linker and have models configured

# Multiserver (Optional)
MULTISERVER_ENABLED = False
MULTISERVER_REDIS_SERVER = os.getenv('MULTISERVER_REDIS_SERVER', '127.0.0.1')
MULTISERVER_REDIS_PORT = int(os.getenv('MULTISERVER_REDIS_PORT', 6379))
MULTISERVER_REDIS_DB = int(os.getenv('MULTISERVER_REDIS_DB', 0))
MULTISERVER_REDIS_EVENT_CHANNEL = "msync"
MULTISERVER_REDIS_CONFIRM_CHANNEL = "mconfirm"

# Data Paths (Adjusted defaults for Render)
SEFARIA_DATA_PATH = os.getenv('SEFARIA_DATA_PATH', '/app/data') # Adjusted default for Render
SEFARIA_EXPORT_PATH = os.getenv('SEFARIA_EXPORT_PATH', '/app/data/export') # Adjusted default for Render

# Google Analytics/Tag Manager (Optional)
GOOGLE_GTAG = os.getenv('GOOGLE_GTAG', None)
GOOGLE_TAG_MANAGER_CODE = os.getenv('GOOGLE_TAG_MANAGER_CODE', None)
HOTJAR_ID = os.getenv('HOTJAR_ID', None)

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': True,
    'SIGNING_KEY': os.getenv('SIMPLE_JWT_SIGNING_KEY', 'a signing key: at least 256 bits'), # Use env var or fallback
}

# Celery (Optional)
CELERY_ENABLED = False
# If enabling, configure BROKER_URL using REDIS_URL
# BROKER_URL = f'{REDIS_URL}/{os.getenv("CELERY_REDIS_BROKER_DB_NUM", 2)}'
# CELERY_RESULT_BACKEND = f'{REDIS_URL}/{os.getenv("CELERY_REDIS_RESULT_BACKEND_DB_NUM", 3)}'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'UTC' # Match your Render/Django TIME_ZONE or keep UTC
CELERY_REDIS_BROKER_DB_NUM = int(os.getenv("CELERY_REDIS_BROKER_DB_NUM", 2)) # Use env vars for consistency if enabling Celery
CELERY_REDIS_RESULT_BACKEND_DB_NUM = int(os.getenv("CELERY_REDIS_RESULT_BACKEND_DB_NUM", 3)) # Use env vars for consistency if enabling Celery
CELERY_QUEUES = {} # Define queues if enabling Celery


# Logging Configuration (Copied from your previous version and example)
# Note: The original example had complex structlog configuration that might depend on sefaria.system.logging
# If the import `from sefaria.system import logging as sefaria_logging` fails, you may need to simplify this section
# or adjust the import path. Using standard `logging` might be safer for initial deployment.
# The config below uses standard logging handlers logging to console (stdout for Render).
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # ADDED filters dictionary
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        # Add other filters if needed and defined in your original settings.py
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
         "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO', # Use INFO or DEBUG for more detailed logs during troubleshooting
            'class': 'logging.StreamHandler',
            'formatter': 'json_formatter', # Or 'verbose' or 'simple'
            'stream': sys.stdout, # Log to standard output, which Render captures
        },
        'mail_admins': { # Configured but requires email settings and DEBUG=False
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'], # This filter is now defined above
        },
        # Add other handlers if needed and defined in your original settings.py
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO', # Use INFO or DEBUG for more detailed logs during troubleshooting
            'propagate': False,
        },
        'sefaria': { # Logger for your Sefaria specific code
             'handlers': ['console'],
             'level': 'INFO', # Use INFO or DEBUG for more detailed logs during troubleshooting
             'propagate': False,
        },
         '': { # Root logger
            'handlers': ['console'],
            'level': 'WARNING', # Set a higher level like WARNING in production typically
            'propagate': False,
        },
        # Add other loggers if needed and defined in your original settings.py
    }
}


# Structured Logging (Structlog) Configuration (Copied from your previous version)
# Note: This might depend on the sefaria.system.logging import.
# If the import fails, you may need to comment out this section or adjust the import.
try:
    # Attempt to import sefaria_logging components
    import sefaria.system.logging as sefaria_logging_system
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.stdlib.add_logger_name,
            sefaria_logging_system.add_severity, # May depend on sefaria_logging_system
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            sefaria_logging_system.log_exception_info, # May depend on sefaria_logging_system
            structlog.processors.UnicodeDecoder(),
            sefaria_logging_system.decompose_request_info, # May depend on sefaria_logging_system
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
except ImportError:
    # Fallback or simplified structlog config if sefaria.system.logging cannot be imported
    # You might want to log a warning here that the full structlog config is not active
    print("Warning: Could not import sefaria.system.logging. Using simplified structlog configuration.")
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.ExceptionPrettyPrinter(),
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

# GeoIP (Optional) - Include these from your example_settings for completeness if needed
# GEOIP_DATABASE = os.getenv('GEOIP_DATABASE', 'data/geoip/GeoLiteCity.dat')
# GEOIPV6_DATABASE = os.getenv('GEOIPV6_DATABASE', 'data/geoip/GeoLiteCityv6.dat')

# RAW_REF_MODEL_BY_LANG_FILEPATH (Optional) - Include these from your example_settings for completeness if needed
# RAW_REF_MODEL_BY_LANG_FILEPATH = {
#     "en": None,
#     "he": None
# }

# RAW_REF_PART_MODEL_BY_LANG_FILEPATH (Optional) - Include these from your example_settings for completeness if needed
# RAW_REF_PART_MODEL_BY_LANG_FILEPATH = {
#     "en": None,
#     "he": None,
# }

# Fail gracefully (Set to True for production)
FAIL_GRACEFULLY = True


# Mobile App Key (Optional) - Include this from your example_settings for completeness if needed
# MOBILE_APP_KEY = os.getenv('MOBILE_APP_KEY', 'MOBILE_APP_KEY')

# Strapi CMS (Optional) - Include these from your example_settings for completeness if needed
# STRAPI_LOCATION = os.getenv('STRAPI_LOCATION', None)
# STRAPI_PORT = os.getenv('STRAPI_PORT', None)

# Cloudflare (Optional) - Include these from your example_settings for completeness if needed
# CLOUDFLARE_ZONE = os.getenv('CLOUDFLARE_ZONE', '')
# CLOUDFLARE_EMAIL = os.getenv('CLOUDFLARE_EMAIL', '')
# CLOUDFLARE_TOKEN = os.getenv('CLOUDFLARE_TOKEN', '')

# Slack (Optional) - Include this from your example_settings for completeness if needed
# SLACK_URL = os.getenv('SLACK_URL', '')
