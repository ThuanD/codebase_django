from .common import *  # NOQA NOSONAR

# Application definition
DJANGO_APPS += [
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS += [
    "constance.backends.memory",
    "django_extensions",
    "drf_spectacular",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# django-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "[APP][TESTING] API Documentation",
    "DESCRIPTION": "",
    "VERSION": "1.0.0",
    "SERVE_PUBLIC": False,
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/",
}

LOGGING = get_logging_config("DEBUG", 3)

# django-constance
CONSTANCE_BACKEND = "constance.backends.memory.MemoryBackend"

# Schema
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"
