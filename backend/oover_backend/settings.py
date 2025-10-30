"""
Django Settings for Oover Backend

This module contains all Django configuration for the Oover sport prediction
application, including database connections, middleware, apps, and security settings.

For production deployment, ensure all sensitive data is stored in environment variables.

Author: Oover Development Team
Date: October 2025
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-key-change-this-in-production'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'django_filters',  # Required for DRF filtering
    
    # Local apps
    'apps.core',
    'api_integrations',  # API integrations module
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS must be before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'oover_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'oover_backend.wsgi.application'


# ==============================================================================
# DATABASE CONFIGURATION (Supabase PostgreSQL)
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'db.rmyxqqcozxbapyldeicm.supabase.co'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',  # Required for Supabase
        },
        'CONN_MAX_AGE': 600,  # Connection pooling (10 minutes)
    }
}


# ==============================================================================
# PASSWORD VALIDATION
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# ==============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# ==============================================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']


# ==============================================================================
# MEDIA FILES (User Uploads)
# ==============================================================================

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ==============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# DJANGO REST FRAMEWORK CONFIGURATION
# ==============================================================================

REST_FRAMEWORK = {
    # Renderers (how data is returned)
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # For dev only
    ],
    
    # Parsers (how data is accepted)
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    
    # Permissions
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Change to IsAuthenticated in production
    ],
    
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    
    # Filtering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',  # Django-filters integration
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Schema generation
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    # Exception handling
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    
    # Date/time formats
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S.%fZ',
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S',
    
    # API rate limiting
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}


# ==============================================================================
# CORS CONFIGURATION (Cross-Origin Resource Sharing)
# ==============================================================================

# Allow requests from Next.js frontend
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Next.js dev server
    'http://127.0.0.1:3000',
]

# Allow credentials (cookies, authorization headers)
CORS_ALLOW_CREDENTIALS = True

# Allow all HTTP methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allow common headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


# ==============================================================================
# DRF SPECTACULAR (OpenAPI/Swagger Documentation)
# ==============================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'Oover API',
    'DESCRIPTION': 'Sport Prediction API - Analyze matches and predict outcomes',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    
    # Swagger UI settings
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    
    # API grouping
    'TAGS': [
        {'name': 'Countries', 'description': 'Country management endpoints'},
        {'name': 'Leagues', 'description': 'League management endpoints'},
        {'name': 'Teams', 'description': 'Team management endpoints'},
        {'name': 'Matches', 'description': 'Match management endpoints'},
        {'name': 'Predictions', 'description': 'Prediction endpoints'},
        {'name': 'API Integrations', 'description': 'External API integration endpoints'},
    ],
}


# ==============================================================================
# CACHE CONFIGURATION
# ==============================================================================

# Cache backend selection based on environment variable
_cache_backend = os.getenv('CACHE_BACKEND', 'locmem')

if _cache_backend == 'redis':
    # Redis cache (production)
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': os.getenv(
                    'CACHE_REDIS_CLIENT_CLASS',
                    'django_redis.client.DefaultClient'
                ),
                'PARSER_CLASS': 'redis.connection.HiredisParser',
                'CONNECTION_POOL_CLASS_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
            },
            'KEY_PREFIX': os.getenv('CACHE_KEY_PREFIX', 'oover_api'),
        }
    }
elif _cache_backend == 'memcached':
    # Memcached cache (production)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
            'LOCATION': '127.0.0.1:11211',
            'KEY_PREFIX': os.getenv('CACHE_KEY_PREFIX', 'oover_api'),
        }
    }
else:
    # Local memory cache (development only)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'oover-cache',
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
            },
        }
    }

# Cache TTL (Time To Live) settings
CACHE_TTL = {
    'ONE_TIME': int(os.getenv('CACHE_TTL_ONE_TIME', 2592000)),  # 30 days
    'PERIODIC': int(os.getenv('CACHE_TTL_PERIODIC', 86400)),     # 1 day
    'SHORT': int(os.getenv('CACHE_TTL_SHORT', 3600)),           # 1 hour
}


# ==============================================================================
# API INTEGRATIONS CONFIGURATION
# ==============================================================================

# Football-Data.org API (Primary Provider)
FOOTBALL_DATA_CONFIG = {
    'API_KEY': os.getenv('FOOTBALL_DATA_API_KEY', ''),
    'BASE_URL': os.getenv('FOOTBALL_DATA_BASE_URL', 'https://api.football-data.org/v4'),
    'RATE_LIMIT': {
        'PER_MINUTE': int(os.getenv('FOOTBALL_DATA_RATE_LIMIT_PER_MINUTE', 10)),
        'PER_DAY': int(os.getenv('FOOTBALL_DATA_RATE_LIMIT_PER_DAY', 14400)),
    },
    'TIMEOUT': int(os.getenv('API_REQUEST_TIMEOUT', 30)),
    'MAX_RETRIES': int(os.getenv('API_MAX_RETRIES', 3)),
    'RETRY_BACKOFF_FACTOR': int(os.getenv('API_RETRY_BACKOFF_FACTOR', 2)),
}

# API-Football API (Fallback Provider)
API_FOOTBALL_CONFIG = {
    'API_KEY': os.getenv('API_FOOTBALL_KEY', ''),
    'BASE_URL': os.getenv('API_FOOTBALL_BASE_URL', 'https://api-football-v1.p.rapidapi.com/v3'),
    'HOST': os.getenv('API_FOOTBALL_HOST', 'api-football-v1.p.rapidapi.com'),
    'RATE_LIMIT': {
        'PER_MINUTE': int(os.getenv('API_FOOTBALL_RATE_LIMIT_PER_MINUTE', 100)),
        'PER_DAY': int(os.getenv('API_FOOTBALL_RATE_LIMIT_PER_DAY', 100)),
    },
    'TIMEOUT': int(os.getenv('API_REQUEST_TIMEOUT', 30)),
    'MAX_RETRIES': int(os.getenv('API_MAX_RETRIES', 3)),
    'RETRY_BACKOFF_FACTOR': int(os.getenv('API_RETRY_BACKOFF_FACTOR', 2)),
}

# API Provider Registry
API_PROVIDERS = {
    'FOOTBALL_DATA': {
        'NAME': 'Football-Data.org',
        'CONFIG': FOOTBALL_DATA_CONFIG,
        'PRIORITY': 1,  # Higher priority = used first
        'ENABLED': bool(FOOTBALL_DATA_CONFIG['API_KEY']),
    },
    'API_FOOTBALL': {
        'NAME': 'API-Football',
        'CONFIG': API_FOOTBALL_CONFIG,
        'PRIORITY': 2,  # Fallback provider
        'ENABLED': bool(API_FOOTBALL_CONFIG['API_KEY']),
    },
}

# Default cache settings for API data
API_CACHE_SETTINGS = {
    'ENABLED': True,
    'KEY_PREFIX': os.getenv('CACHE_KEY_PREFIX', 'oover_api'),
    'DEFAULT_TTL': CACHE_TTL['ONE_TIME'],
}


# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'api_file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'api_integrations.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',  # Change to DEBUG to see SQL queries
            'propagate': False,
        },
        'api_integrations': {
            'handlers': ['console', 'api_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# ==============================================================================
# SECURITY SETTINGS FOR PRODUCTION
# ==============================================================================

if not DEBUG:
    # HTTPS settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Security headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
