from pathlib import Path
from typing import List, Optional

from pydantic import AnyHttpUrl, EmailStr, Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def get_logging_config(
    log_level: str = "INFO", backup_count: int = 10, max_bytes: int = 5242880
) -> dict:
    """Get logging configuration based on log level."""
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
    """Env settings."""

    # Django settings
    DJANGO_SETTINGS_MODULE: str = Field(..., description="Django settings module")
    DEBUG: bool = Field(False, description="Enable debug mode")
    SECRET_KEY: str = Field(..., description="Secret key for Django")

    # Host settings
    ALLOWED_HOSTS: List[str] = Field(description="List of allowed hosts")
    CORS_ALLOWED_ORIGINS: List[AnyHttpUrl] = Field(description="CORS allowed origins")
    CSRF_TRUSTED_ORIGINS: List[AnyHttpUrl] = Field(description="CSRF trusted origins")

    # Email settings
    EMAIL_HOST: str = Field("smtp.gmail.com", description="Email host")
    EMAIL_PORT: int = Field(587, description="Email port")
    EMAIL_USE_TLS: bool = Field(True, description="Use TLS for email")
    EMAIL_USE_SSL: bool = Field(False, description="Use SSL for email")
    EMAIL_HOST_USER: Optional[EmailStr] = Field(None, description="Email host user")
    EMAIL_HOST_PASSWORD: Optional[str] = Field(None, description="Email host password")
    DEFAULT_FROM_EMAIL: Optional[str] = Field(None, description="Default from email")
