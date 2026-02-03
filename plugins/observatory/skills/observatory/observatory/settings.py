"""
Django settings for Claude Code Observatory.

PostgreSQL with pgvector for embeddings support.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-observatory-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
# Default to False for security - explicitly set DEBUG=True for development
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'django_filters',
    'drf_spectacular',
    'corsheaders',
    # Local apps - Claude Code domain
    'sessions.apps.SessionsConfig',  # Use explicit config to avoid conflict with django.contrib.sessions
    'plugins',
    'skills',
    'commands',
    'agents',
    'hooks',
    'settings.apps.SettingsConfig',  # Use explicit config to avoid name conflict
    'output_styles',
    'mcps',
    # Knowledge graph
    'knowledge',
    # Cost tracking
    'billing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS must be before CommonMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'observatory.urls'

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

WSGI_APPLICATION = 'observatory.wsgi.application'

# Database - PostgreSQL with pgvector
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgres://localhost/claude_observatory')

# Parse DATABASE_URL
if DATABASE_URL.startswith('postgres'):
    import re
    match = re.match(
        r'postgres(?:ql)?://(?:(?P<user>[^:]+)(?::(?P<password>[^@]+))?@)?(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<name>.+)',
        DATABASE_URL
    )
    if match:
        db_config = match.groupdict()
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': db_config['name'],
                'USER': db_config.get('user') or os.environ.get('USER', 'postgres'),
                'PASSWORD': db_config.get('password') or '',
                'HOST': db_config.get('host') or 'localhost',
                'PORT': db_config.get('port') or '5432',
            }
        }
    else:
        # Fallback to defaults
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'claude_observatory',
                'USER': os.environ.get('USER', 'postgres'),
                'PASSWORD': '',
                'HOST': 'localhost',
                'PORT': '5432',
            }
        }
else:
    # SQLite fallback (no pgvector support)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'observatory.db',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# DRF Spectacular (OpenAPI/Swagger)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Claude Code Observatory API',
    'DESCRIPTION': 'Complete REST API for Claude Code data - sessions, messages, hooks, plugins, settings, subagents, and knowledge graph.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# CORS Configuration
# For development, allow localhost origins
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ORIGINS',
    'http://localhost:3000,http://localhost:5173,http://localhost:8080'
).split(',')

# Allow credentials for authenticated API access
CORS_ALLOW_CREDENTIALS = True

# In development, can also use CORS_ALLOW_ALL_ORIGINS = True (not recommended for production)
