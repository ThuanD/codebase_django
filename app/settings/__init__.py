from pathlib import Path
from typing import List, Optional

from pydantic import AnyHttpUrl, EmailStr, Field, PositiveInt, SecretStr
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def get_logging_config(
    log_level: str = "INFO", backup_count: int = 10, max_bytes: int = 5242880
) -> dict:
    """Get logging configuration based on log level.

    Args:
        log_level: The logging level (e.g., "DEBUG", "INFO", "WARNING").
        backup_count: The number of backup log files to keep.
        max_bytes: The maximum size of a log file before rotation.

    Returns:
        A dictionary containing the logging configuration.

    """
    log_path = Path(BASE_DIR) / "logs"
    log_path.mkdir(parents=True, exist_ok=True)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[%(levelname)s] %(asctime)s [%(name)s:%(lineno)s] "
                "%(module)s.%(funcName)s(): %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            # "json": {
            #     "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            #     "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            #     "datefmt": "%Y-%m-%d %H:%M:%S"
            # },
            "simple": {
                "format": "[%(levelname)s] %(asctime)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "file": {
                "filters": [],
                "class": "logging.handlers.RotatingFileHandler",
                "filename": BASE_DIR / "logs/backend.log",
                "maxBytes": max_bytes,
                "backupCount": backup_count,
                "formatter": "verbose",
            },
            "sql": {
                "level": "DEBUG",
                "filters": [],
                "class": "logging.handlers.RotatingFileHandler",
                "filename": BASE_DIR / "logs/sql.log",
                "maxBytes": max_bytes,
                "backupCount": backup_count,
                "formatter": "simple",
            },
        },
        "loggers": {
            "django.request": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": True,
            },
            "django.db.backends": {
                "handlers": ["sql"],
                "level": log_level,
                "propagate": False,
            },
            "app": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "apps": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "tests": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    }


class EnvSettings(BaseSettings):
    """Environment settings for the application."""

    # Django settings
    DJANGO_SETTINGS_MODULE: str = Field(..., description="Django settings module")
    DEBUG: bool = Field(False, description="Enable debug mode")
    SECRET_KEY: SecretStr = Field(..., description="Secret key for Django")

    # Host settings
    ALLOWED_HOSTS: List[str] = Field(..., description="List of allowed hosts")
    CORS_ALLOWED_ORIGINS: List[AnyHttpUrl] = Field(..., description="CORS allowed origins")
    CSRF_TRUSTED_ORIGINS: List[AnyHttpUrl] = Field(..., description="CSRF trusted origins")

    # Database settings
    DATABASE_URL: Optional[str] = Field(None, description="Database connection URL")

    # Cache settings
    CACHE_URL: Optional[str] = Field(None, description="Cache connection URL")

    # Email settings
    EMAIL_HOST: str = Field("smtp.gmail.com", description="Email host")
    EMAIL_PORT: PositiveInt = Field(587, description="Email port")
    EMAIL_USE_TLS: bool = Field(True, description="Use TLS for email")
    EMAIL_USE_SSL: bool = Field(False, description="Use SSL for email")
    EMAIL_HOST_USER: Optional[EmailStr] = Field(None, description="Email host user")
    EMAIL_HOST_PASSWORD: Optional[SecretStr] = Field(None, description="Email host password")
    DEFAULT_FROM_EMAIL: Optional[str] = Field(None, description="Default from email")

    # Health Check Endpoint
    HEALTH_CHECK_ENDPOINT: str = Field(
        "/api/health_check/", description="URL for the health check endpoint"
    )

    # Docker settings only
    GUNICORN_WORKERS: PositiveInt = Field(4, description="Number of Gunicorn workers")
    GUNICORN_TIMEOUT: PositiveInt = Field(120, description="Gunicorn request timeout in seconds")
    GUNICORN_KEEP_ALIVE: PositiveInt = Field(5, description="Gunicorn keep-alive time in seconds")

    UPDATE_DEPENDENCIES: bool = Field(True, description="Update dependencies on startup")
    RUN_MIGRATIONS: bool = Field(True, description="Run database migrations on startup")
    RUN_COLLECTSTATIC: bool = Field(True, description="Run collectstatic on startup")
    SKIP_SETUP: bool = Field(False, description="Skip all setup steps if true")
