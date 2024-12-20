from unittest import TestCase
from unittest.mock import patch

from constance import config as constance_config
from django.conf import settings
from django.test import override_settings

from app.config import config


class TestConfigWrapper(TestCase):
    """Test the ConfigWrapper class."""

    def tearDown(self) -> None:
        """Reset the config cache."""
        config.reset()

    @override_settings(MAINTENANCE_ENABLE=False)
    def test_constance_value(self) -> None:
        """Test the constance value."""
        self.assertFalse(constance_config.MAINTENANCE_ENABLE)
        self.assertFalse(settings.MAINTENANCE_ENABLE)
        self.assertFalse(config.MAINTENANCE_ENABLE)

    def test_constance_missing_key(self) -> None:
        """Test when the constance key is missing."""
        with self.assertRaises(AttributeError):
            _ = constance_config.DEBUG
        self.assertEqual(config.DEBUG, settings.DEBUG)

    def test_config_missing_key(self) -> None:
        """Test when the config key is missing."""
        with self.assertRaises(AttributeError):
            _ = config.MISSING_KEY

    @override_settings(MAINTENANCE_ENABLE=False)
    def test_update_constance_config(self) -> None:
        """Test updating the constance config."""
        self.assertEqual(constance_config.MAINTENANCE_ENABLE, False)
        constance_config.MAINTENANCE_ENABLE = True
        self.assertEqual(config.MAINTENANCE_ENABLE, True)

    @patch.dict("sys.modules", {"constance": None})
    def test_import_error_handling(self) -> None:
        """Test handling import errors."""
        from app.config import ConfigWrapper

        config_wrapper = ConfigWrapper()
        self.assertIsNone(config_wrapper.constance_config)
        self.assertIsNone(config_wrapper.constance_settings)
