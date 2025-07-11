"""Django settings for care_im_bot project."""

import os
import logging.config
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-cr)^11*p&up$d#pp^-c65+aawz%wo*ub-m8&lob@@kwyp3jgvn')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'


ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = ALLOWED_HOSTS_ENV.split(',') if ALLOWED_HOSTS_ENV else ["localhost", "127.0.0.1"]


if "whatsapp-bot.botforcare.social" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("whatsapp-bot.botforcare.social")


from fnmatch import fnmatch
BOT_DOMAIN = "whatsapp-bot.botforcare.social"
for host in list(ALLOWED_HOSTS):
    if host.startswith('*.'):
        wildcard_pattern = host.replace('*.', '')
        if fnmatch(BOT_DOMAIN, f"*.{wildcard_pattern}"):

            break
else:

    if BOT_DOMAIN not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(BOT_DOMAIN)


NGROK_URL = os.environ.get('NGROK_URL', '')
if NGROK_URL and NGROK_URL not in ALLOWED_HOSTS:

    from urllib.parse import urlparse
    ngrok_host = urlparse(NGROK_URL).netloc
    ALLOWED_HOSTS.append(ngrok_host)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "whatsapp_bot",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "care_im_bot.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "care_im_bot.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    }
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/care_whatsapp_bot.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'whatsapp_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/whatsapp.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/error.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'whatsapp_bot': {
            'handlers': ['console', 'whatsapp_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'bot_engine': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'care_wrapper': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'env_validator': {
            'handlers': ['console', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

# WhatsApp Business API Configuration
WHATSAPP_BUSINESS_API = {
    'ACCESS_TOKEN': os.environ.get('WHATSAPP_ACCESS_TOKEN', ''),
    'PHONE_NUMBER_ID': os.environ.get('WHATSAPP_PHONE_NUMBER_ID', ''),
    'WEBHOOK_VERIFY_TOKEN': os.environ.get('WHATSAPP_WEBHOOK_VERIFY_TOKEN', ''),
    'API_VERSION': 'v22.0',
    'BASE_URL': f'https://graph.facebook.com/v22.0'
}

# CARE API Configuration
CARE_API = {
    'BASE_URL': os.environ.get('CARE_API_BASE_URL', ''),
    'API_KEY': os.environ.get('CARE_API_KEY', '')
}