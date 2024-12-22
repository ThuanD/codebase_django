import os
import unittest
from unittest.mock import MagicMock, patch

from manage import _get_django_setting_module


class TestGetDjangoSettingModule(unittest.TestCase):
    """Test suite for Django settings module resolution functionality.

    This test suite verifies the behavior of _get_django_setting_module function
    under different scenarios including command line arguments and environment
    variables.
    """

    @patch("manage._get_django_setting_module")
    @patch.dict("os.environ", {}, clear=True)
    def test_django_import_error(self, mock_get_settings: MagicMock) -> None:
        """Test Django import error handling.

        Verifies that appropriate error is raised when Django is not installed
        or not available in PYTHONPATH.

        Args:
            mock_get_settings: Mock object for _get_django_setting_module function.

        Returns:
            None
        """
        mock_get_settings.return_value = "app.settings.local"

        with patch.dict("sys.modules", {"django.core.management": None}):
            with self.assertRaises(ImportError) as context:
                from manage import main

                main()

        expected_error = (
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
        self.assertIn(expected_error, str(context.exception))

    @patch("argparse.ArgumentParser.parse_known_args")
    def test_settings_from_command_line(self, mock_parse_known_args: MagicMock) -> None:
        """Test settings module resolution from command line arguments.

        Verifies that settings module is correctly resolved when provided
        via --settings command line argument.

        Args:
            mock_parse_known_args: Mock object for ArgumentParser.parse_known_args.

        Returns:
            None
        """
        # Setup mock arguments
        mock_args = MagicMock()
        mock_args.settings = "app.settings.production"
        mock_parse_known_args.return_value = (mock_args, None)

        # Execute function under test
        result = _get_django_setting_module()

        # Verify result
        self.assertEqual(result, "app.settings.production")

    @patch("argparse.ArgumentParser.parse_known_args")
    def test_settings_from_env_file(self, mock_parse_known_args: MagicMock) -> None:
        """Test settings module resolution from environment file.

        Verifies that settings module is correctly resolved when
        DJANGO_SETTINGS_MODULE is set in the environment.

        Args:
            mock_parse_known_args: Mock object for ArgumentParser.parse_known_args.

        Returns:
            None
        """
        # Setup environment and mock arguments
        os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings.staging"
        mock_args = MagicMock()
        mock_args.settings = None
        mock_parse_known_args.return_value = (mock_args, None)

        # Execute function under test
        result = _get_django_setting_module()

        # Verify result
        self.assertEqual(result, "app.settings.staging")

    @patch("argparse.ArgumentParser.parse_known_args")
    def test_default_settings(self, mock_parse_known_args: MagicMock) -> None:
        """Test Django settings module resolution with default configuration.

        This test verifies that when no --settings argument is provided and
        DJANGO_SETTINGS_MODULE is not set in the environment, the function returns
        the default settings module path.

        Args:
            mock_parse_known_args: Mock object for ArgumentParser.parse_known_args.

        Returns:
            None
        """
        # Setup mock arguments
        mock_args = MagicMock()
        mock_args.settings = None
        mock_parse_known_args.return_value = (mock_args, [])

        # Execute function under test
        result = _get_django_setting_module(".env.mock")

        # Verify result
        self.assertEqual(result, "app.settings.local")
