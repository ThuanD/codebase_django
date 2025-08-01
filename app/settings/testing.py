from .common import *  # NOQA NOSONAR

# Application definition
DJANGO_APPS += [
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS += [
    "constance.backends.database",
    "django_extensions",
    "drf_spectacular",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

# django-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "[APP][TESTING] API Documentation",
    "DESCRIPTION": "",
    "VERSION": "1.0.0",
    "SERVE_PUBLIC": False,
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/",
}

# Schema
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"

EMAIL_SUBJECT_PREFIX = "[APP][TESTING]"

LOGGING = get_logging_config("DEBUG", 30)
