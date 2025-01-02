import unittest
from unittest.mock import MagicMock, patch

from app import wsgi


class TestWSGI(unittest.TestCase):
    """Test the WSGI module."""

    @patch("app.wsgi.argparse.ArgumentParser")
    def test_settings_from_command_line(self, mock_argparse: MagicMock):
        """Test when --env argument is provided."""
        mock_args = MagicMock()
        mock_args.env = "app.settings.production"
        mock_argparse.return_value.parse_known_args.return_value = (mock_args, None)

        result = wsgi.get_django_setting_module()
        self.assertEqual(result, "app.settings.production")

    @patch("app.wsgi.load_dotenv")
    @patch("app.wsgi.os.getenv")
    @patch("app.wsgi.argparse.ArgumentParser")
    def test_settings_from_env_file(
        self,
        mock_argparse: MagicMock,
        mock_getenv: MagicMock,
        mock_load_dotenv: MagicMock,
    ):
        """Test when --env argument is not provided and .env file exists."""
        mock_args = MagicMock()
        mock_args.env = None
        mock_argparse.return_value.parse_known_args.return_value = (mock_args, None)
        mock_load_dotenv.return_value = True
        mock_getenv.return_value = "app.settings.staging"
        result = wsgi.get_django_setting_module()
        self.assertEqual(result, "app.settings.staging")

    @patch("app.wsgi.load_dotenv")
    @patch("app.wsgi.argparse.ArgumentParser")
    def test_default_settings(
        self, mock_argparse: MagicMock, mock_load_dotenv: MagicMock
    ):
        """Test when --env argument is not provided and .env file doesn't exist."""
        mock_args = MagicMock()
        mock_args.env = None
        mock_argparse.return_value.parse_known_args.return_value = (mock_args, None)
        mock_load_dotenv.return_value = False

        result = wsgi.get_django_setting_module()
        self.assertEqual(result, "app.settings.local")
