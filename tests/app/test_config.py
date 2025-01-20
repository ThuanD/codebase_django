from unittest import TestCase
from unittest.mock import patch

from django.conf import settings
from django.test import override_settings

from constance import config as constance_config

from app.contrib.config import config


class TestConfigWrapper(TestCase):
    """Test the ConfigWrapper class."""

    def tearDown(self):
        """Reset the config cache."""
        config.reset()

    @override_settings(MAINTENANCE_ENABLE=False)
    def test_constance_value(self):
        """Test retrieving a value from constance."""
        self.assertFalse(constance_config.MAINTENANCE_ENABLE)
        self.assertFalse(settings.MAINTENANCE_ENABLE)
        self.assertFalse(config.MAINTENANCE_ENABLE)

    def test_constance_missing_key(self):
        """Test accessing a missing key in constance."""
        with self.assertRaises(AttributeError):
            _ = constance_config.MISSING_KEY
        self.assertEqual(config.DEBUG, settings.DEBUG)  # Fallback to settings

    def test_config_missing_key(self):
        """Test accessing a missing key in config (no fallback in settings)."""
        with self.assertRaises(AttributeError):
            _ = config.MISSING_KEY

    @override_settings(MAINTENANCE_ENABLE=False)
    def test_update_constance_config(self):
        """Test updating a constance config value."""
        self.assertFalse(constance_config.MAINTENANCE_ENABLE)
        constance_config.MAINTENANCE_ENABLE = True
        self.assertTrue(config.MAINTENANCE_ENABLE)

    @patch.dict("sys.modules", {"constance": None})
    def test_import_error_handling(self):
        """Test handling import errors when constance is not available."""
        from app.contrib.config import ConfigWrapper

        config_wrapper = ConfigWrapper()
        self.assertIsNone(config_wrapper.constance_config)
        self.assertIsNone(config_wrapper.constance_settings)

    def test_reset(self):
        """Test the reset method to ensure config values are reset to defaults."""
        # Change a config value
        constance_config.MAINTENANCE_ENABLE = True
        self.assertTrue(config.MAINTENANCE_ENABLE)

        # Reset the config
        config.reset()

        # Check if the value is reset to the default
        self.assertFalse(constance_config.MAINTENANCE_ENABLE)
