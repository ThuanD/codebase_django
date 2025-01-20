import json
from unittest import TestCase
from unittest.mock import Mock, patch

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse

from constance import config as constance_config
from rest_framework import status

from app.contrib.config import config
from app.contrib.exception import ServiceUnavailable
from app.contrib.health_check.middleware import (
    HealthCheckMiddleware,
    MaintenanceMiddleware,
)


class TestHealthCheckMiddleware(TestCase):
    """Test suite for the HealthCheckMiddleware."""

    def setUp(self):
        """Set up the test environment before each test method."""
        self.get_response = Mock(return_value=HttpResponse())
        self.middleware = HealthCheckMiddleware(self.get_response)

    def tearDown(self):
        """Clear the cache after each test."""
        cache.clear()

    def test_health_check_path(self):
        """Test that the middleware returns a 200 status code for the health check."""
        request = HttpRequest()
        request.path = "/api/health_check/"  # Update to use the constant
        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.get_response.assert_not_called()

    def test_non_health_check_path(self):
        """Test that the middleware calls get_response for non-health check paths."""
        request = HttpRequest()
        request.path = "/some-other-path"
        response = self.middleware(request)
        self.get_response.assert_called_once_with(request)
        self.assertEqual(response, self.get_response.return_value)

    def test_health_check_throttle(self):
        """Test that the throttle limit is exceeded."""
        request = HttpRequest()
        request.path = "/api/health_check/"

        self.middleware.throttle.allow_request = Mock(return_value=False)

        response = self.middleware(request)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @patch("app.contrib.health_check.middleware.connection")
    def test_health_check_database_failure(self, mock_connection: Mock):
        """Test that the health check returns a 503 status code on database failure."""
        request = HttpRequest()
        request.path = "/api/health_check/"

        mock_connection.ensure_connection.side_effect = Exception("Database error")

        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        content = json.loads(response.content)
        self.assertEqual(content["code"], ServiceUnavailable.default_code)
        self.assertIn("database", content["message"])

    @patch("app.contrib.health_check.middleware.cache")
    def test_health_check_cache_failure(self, mock_cache: Mock):
        """Test that the health check returns a 503 status code on cache failure."""
        request = HttpRequest()
        request.path = "/api/health_check/"

        mock_cache.get.return_value = None  # Simulate cache miss/failure

        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        content = json.loads(response.content)
        self.assertEqual(content["code"], ServiceUnavailable.default_code)
        self.assertIn("cache", content["message"])


class TestMaintenanceMiddleware(TestCase):
    """Test suite for the MaintenanceMiddleware."""

    def setUp(self):
        """Set up the test environment before each test method."""
        self.get_response = Mock(return_value=HttpResponse())
        self.middleware = MaintenanceMiddleware(self.get_response)

    def tearDown(self):
        """Reset the config to the default values."""
        config.reset()
        cache.clear()

    def test_maintenance_disabled(self):
        """Test middleware behavior when maintenance mode is disabled."""
        constance_config.MAINTENANCE_ENABLE = False
        request = HttpRequest()
        request.path = "/some-path"
        response = self.middleware(request)
        self.get_response.assert_called_once_with(request)
        self.assertEqual(response, self.get_response.return_value)

    def test_maintenance_enable(self):
        """Test middleware behavior when maintenance mode is disabled."""
        constance_config.MAINTENANCE_ENABLE = True
        request = HttpRequest()
        request.path = "/some-path"
        response = self.middleware(request)
        self.assertEqual(response.status_code, ServiceUnavailable.status_code)
        content = json.loads(response.content)
        self.assertEqual(content["code"], ServiceUnavailable.default_code)

    def test_maintenance_enabled_allowed_path(self):
        """Test middleware behavior for allowed paths in maintenance mode."""
        constance_config.MAINTENANCE_ENABLE = True
        constance_config.MAINTENANCE_ALLOWED_URLS = ["/admin/", "/special-api/"]
        request = HttpRequest()
        request.path = "/admin/some/path"
        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.get_response.assert_called_once_with(request)
        self.assertEqual(response, self.get_response.return_value)

        request.path = "/special-api/data"
        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.get_response.assert_called()

    def test_maintenance_enabled_allowed_ip(self):
        """Test middleware behavior for allowed IPs in maintenance mode."""
        constance_config.MAINTENANCE_ENABLE = True
        constance_config.MAINTENANCE_ALLOWED_IPS = ["192.168.1.1", "10.0.0.1"]
        request = HttpRequest()
        request.path = "/some/path"
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.get_response.assert_called_once_with(request)
        self.assertEqual(response, self.get_response.return_value)

        request.META["REMOTE_ADDR"] = "10.0.0.1"
        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.get_response.assert_called()

        request.META["REMOTE_ADDR"] = "10.0.0.2"
        response = self.middleware(request)
        self.assertEqual(response.status_code, ServiceUnavailable.status_code)
        content = json.loads(response.content)
        self.assertEqual(content["code"], ServiceUnavailable.default_code)

    def test_maintenance_enabled_disallowed_path(self):
        """Test middleware behavior for disallowed paths in maintenance mode."""
        constance_config.MAINTENANCE_ENABLE = True
        request = HttpRequest()
        request.path = "/some-path/"
        response = self.middleware(request)
        self.get_response.assert_not_called()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, ServiceUnavailable.status_code)
        content = json.loads(response.content)
        self.assertEqual(content["code"], ServiceUnavailable.default_code)

    @patch("app.contrib.health_check.middleware.config")
    def test_maintenance_enabled_staff_bypass(self, mock_config: Mock):
        """Test that staff users can bypass maintenance mode."""
        mock_config.MAINTENANCE_ENABLE = True
        request = HttpRequest()
        request.path = "/some-path/"
        request.user = Mock(is_staff=True)  # Simulate a staff user
        response = self.middleware(request)
        self.get_response.assert_called_once_with(request)
        self.assertEqual(response, self.get_response.return_value)

    def test_maintenance_custom_message(self):
        """Test that the custom maintenance message is displayed."""
        constance_config.MAINTENANCE_ENABLE = True
        constance_config.MAINTENANCE_MESSAGE = "Custom maintenance message."
        request = HttpRequest()
        request.path = "/some-path/"
        response = self.middleware(request)
        self.assertEqual(response.status_code, ServiceUnavailable.status_code)
        content = json.loads(response.content)
        self.assertEqual(content["code"], ServiceUnavailable.default_code)
        self.assertEqual(content["message"], "Custom maintenance message.")
