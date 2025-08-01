"""Django settings for app project.

Generated by 'django-admin startproject' using Django 4.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import logging
import os
import sys
from pathlib import Path

from django.utils.translation import gettext_lazy as _

from app.settings import EnvSettings, get_logging_config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment should already be set up by manage.py/wsgi.py/asgi.py
django_settings_module = os.getenv("DJANGO_SETTINGS_MODULE")
if not django_settings_module:
    logging.error("\033[91mERROR: DJANGO_SETTINGS_MODULE not set.\033[0m")
    sys.exit(1)

# Extract environment name and construct env file path
env_name = django_settings_module.split(".")[-1]
env_file = BASE_DIR / f".env.{env_name}"
if not env_file.exists():
    env_file = BASE_DIR / ".env"

# Load and validate security configuration
try:
    env_settings = EnvSettings(
        _case_sensitive=False, _env_file=env_file, _env_file_encoding="utf-8"
    )
except Exception as e:
    logging.error("\033[91mERROR: Environment validation error: %s\033[0m", e)
    sys.exit(1)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_settings.DEBUG


def parse_comma_separated_list(value: str) -> list:
    """Parse a comma-separated list of strings into a list of strings."""
    return [item.strip() for item in value.split(",") if item.strip()]


ALLOWED_HOSTS = env_settings.ALLOWED_HOSTS

# SECURITY WARNING: don't allow all origins in production!
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
CORS_ALLOWED_ORIGINS = env_settings.CORS_ALLOWED_ORIGINS

CSRF_TRUSTED_ORIGINS = env_settings.CSRF_TRUSTED_ORIGINS

# Application definition
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
]
THIRD_PARTY_APPS = [
    "constance",
    "corsheaders",
    "django_filters",
    "rest_framework",
]
CUSTOM_APPS = [
    "apps.apidocs",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

MIDDLEWARE = [
    "app.contrib.health_check.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "app.contrib.health_check.middleware.MaintenanceMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "app.contrib.request_logging.middleware.RequestLoggingMiddleware",
    "app.contrib.security.middleware.SecurityHeadersMiddleware",
]

# Session security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"

ROOT_URLCONF = "app.urls"
APPEND_SLASH = True

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

WSGI_APPLICATION = "app.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 12,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# locale
LOCALE_PATHS = (BASE_DIR / "app/locale",)
LANGUAGE_DEFAULT = "en"
LANGUAGES = [
    ("en", _("English")),
    ("vi", _("Vietnamese")),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []

# Media file
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "auth.User"

# django-extensions
SHELL_PLUS = "ipython"
SHELL_PLUS_PRINT_SQL = False
SHELL_PLUS_IMPORTS = [
    "from app.contrib.config import config",
]

LOGGING = get_logging_config("INFO", 100)

REST_FRAMEWORK = {
    # Base API policies
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_VERSIONING_CLASS": None,
    # Generic view behavior
    "DEFAULT_PAGINATION_CLASS": "app.contrib.pagination.CustomPagination",
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    # Throttling
    "DEFAULT_THROTTLE_RATES": {
        "user": "60/minute",
        "anon": "30/minute",
    },
    # Pagination
    "PAGE_SIZE": 20,
    # Versioning
    "DEFAULT_VERSION": "1",
    "ALLOWED_VERSIONS": None,
    "VERSION_PARAM": "version",
    # Exception handling
    "EXCEPTION_HANDLER": "app.contrib.exception.exception_handler",
}

# SMTP Gmail
EMAIL_USE_LOCALTIME = True
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 5  # seconds
EMAIL_PORT = 587
EMAIL_HOST = env_settings.EMAIL_HOST
EMAIL_HOST_USER = env_settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = env_settings.EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = env_settings.DEFAULT_FROM_EMAIL
EMAIL_SUBJECT_PREFIX = "[APP]"

MAINTENANCE_ENABLE = False
MAINTENANCE_MESSAGE = "We are currently undergoing maintenance. We will be back soon."
MAINTENANCE_ALLOWED_URLS = []
MAINTENANCE_ALLOWED_IPS = []

# django-constance
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_CONFIG = {
    # Maintenance configuration
    "MAINTENANCE_ENABLE": (
        MAINTENANCE_ENABLE,  # Default value
        _("Enable maintenance mode"),  # Help text
        bool,  # Type
    ),
    "MAINTENANCE_MESSAGE": (
        MAINTENANCE_MESSAGE,
        _("Message to display during maintenance"),
        str,
    ),
    "MAINTENANCE_ALLOWED_URLS": (
        MAINTENANCE_ALLOWED_URLS,
        _(
            "List of URL patterns allowed during maintenance "
            "(e.g., /admin/, /api/special-endpoint/)"
        ),
        list,
    ),
    "MAINTENANCE_ALLOWED_IPS": (
        MAINTENANCE_ALLOWED_IPS,
        _("List of IP addresses allowed during maintenance"),
        list,
    ),
}
CONSTANCE_CONFIG_FIELDSETS = (
    (
        _("Maintenance Mode Settings"),
        {
            "fields": (
                "MAINTENANCE_ENABLE",
                "MAINTENANCE_MESSAGE",
                "MAINTENANCE_ALLOWED_URLS",
                "MAINTENANCE_ALLOWED_IPS",
            ),
        },
    ),
)

# Endpoint to health check API service
HEALTH_CHECK_ENDPOINT = env_settings.HEALTH_CHECK_ENDPOINT
