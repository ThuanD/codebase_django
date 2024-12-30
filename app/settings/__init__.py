from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def get_logging_config(
    log_level: str = "INFO",
    backup_count: int = 10,
    max_bytes: int = 5242880,  # 5MB
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
