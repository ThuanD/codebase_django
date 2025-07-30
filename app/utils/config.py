import logging
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class DjangoConfigError(Exception):
    """Custom exception for Django configuration errors."""

    pass


def get_base_dir() -> Path:
    """Get the base directory of the project (where manage.py is located)."""
    # From app/utils/config.py, go up one level to reach project root
    return Path(__file__).resolve().parent.parent.parent


def load_env_file(env_name: Optional[str] = None, base_dir: Optional[Path] = None) -> Path:
    """Load environment file based on environment name."""
    if base_dir is None:
        base_dir = get_base_dir()

    env_files_to_try = []

    if env_name:
        env_files_to_try.append(base_dir / f".env.{env_name}")

    env_files_to_try.append(base_dir / ".env")

    for env_file in env_files_to_try:
        if env_file.exists() and load_dotenv(env_file):
            logging.info("Loaded environment from: %s", env_file)
            return env_file

    raise DjangoConfigError("Unable to find any .env file in %s", base_dir)


def get_django_settings_module(from_command_line: bool = True) -> str:
    """Get Django settings module with priority."""
    if from_command_line:
        import argparse

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--settings", help="Django settings module")
        args, _ = parser.parse_known_args()
        if args.settings:
            return args.settings

    # Try environment variable
    settings_module = os.getenv("DJANGO_SETTINGS_MODULE")
    if settings_module:
        return settings_module

    # Default - adjusted to match your structure
    return "app.settings.local"


def setup_django_environment(from_command_line: bool = True) -> tuple[str, Path]:
    """Setup Django environment and return (settings_module, env_file_path)."""
    # Get settings module
    settings_module = get_django_settings_module(from_command_line)
    logging.info("Using settings module: %s", settings_module)

    # Extract environment name from settings module
    # For app.settings.local -> "local"
    # For app.settings.production -> "production"
    env_name = settings_module.split(".")[-1] if "." in settings_module else None

    # Load appropriate .env file
    env_file_path = None
    try:
        env_file_path = load_env_file(env_name)
    except DjangoConfigError as e:
        logging.error("\033[91mERROR: %s\033[0m", e)
        sys.exit(1)

    # Set environment variable
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    return settings_module, env_file_path
