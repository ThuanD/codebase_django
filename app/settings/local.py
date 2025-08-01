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
    "debug_toolbar",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

MIDDLEWARE = [
    "app.contrib.health_check.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "app.contrib.health_check.middleware.MaintenanceMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "app.contrib.request_logging.middleware.RequestLoggingMiddleware",
    "app.contrib.security.middleware.SecurityHeadersMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "app_cache",
    }
}

# django-debug-toolbar
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]
DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
]
SHOW_COLLAPSED = True
TOOLBAR_LANGUAGE = "en-us"
EXTRA_SIGNALS = []

# django-extensions
SHELL_PLUS_PRINT_SQL = True

# django-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "[APP][LOCAL] API Documentation",
    "DESCRIPTION": "",
    "VERSION": "1.0.0",
    "SERVE_PUBLIC": False,
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/",
}

LOGGING = get_logging_config("DEBUG", 10)

# django-constance
CONSTANCE_BACKEND = "constance.backends.memory.MemoryBackend"

# Schema
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"
