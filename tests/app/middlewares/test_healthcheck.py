import json
from unittest import TestCase
from unittest.mock import Mock

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.test import override_settings

from constance import config as constance_config
from rest_framework.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from app.config import config
from app.contrib.health_check.middleware import (
    HealthCheckMiddleware,
    MaintenanceMiddleware,
)


class TestHealthCheckMiddleware(TestCase):
    """Test suite for the HealthCheckMiddleware."""

    def setUp(self) -> None:
        """Set up the test environment before each test method."""
        self.get_response = Mock(return_value=HttpResponse())
        self.middleware = HealthCheckMiddleware(self.get_response)

    def test_health_check_path(self) -> None:
        """Test that the middleware returns a 200 status code for the health check."""
        request = HttpRequest()
        request.path = "/api/health_check/"
        response = self.middleware(request)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.get_response.assert_not_called()

    def test_non_health_check_path(self) -> None:
        """Test that the middleware calls get_response for non-health check paths."""
        request = HttpRequest()
        request.path = "/some-other-path"
        response = self.middleware(request)
        self.get_response.assert_called_once_with(request)
        self.assertEqual(response, self.get_response.return_value)


class TestMaintenanceMiddleware(TestCase):
    """Test suite for the MaintenanceMiddleware."""

    def setUp(self) -> None:
        """Set up the test environment before each test method."""
        self.get_response = Mock(return_value=HttpResponse())
        self.middleware = MaintenanceMiddleware(self.get_response)

    def tearDown(self) -> None:
        """Reset the config to the default values."""
        config.reset()

    def test_maintenance_disabled(self) -> None:
        """Test middleware behavior when maintenance mode is disabled."""
        constance_config.MAINTENANCE_ENABLE = False
        request = HttpRequest()
        request.path = "/some-path"
        response = self.middleware(request)
        self.get_response.assert_called_once_with(request)
        self.assertEqual(response, self.get_response.return_value)

    def test_maintenance_enabled_allowed_path(self) -> None:
        """Test middleware behavior for allowed paths in maintenance mode."""
        constance_config.MAINTENANCE_ENABLE = True
        request = HttpRequest()
        request.path = "/admin/"  # Assuming "/admin" is in allowed_paths
        response = self.middleware(request)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.get_response.assert_called_once_with(request)
        self.assertEqual(response, self.get_response.return_value)

    def test_maintenance_enabled_disallowed_path(self) -> None:
        """Test middleware behavior for disallowed paths in maintenance mode."""
        constance_config.MAINTENANCE_ENABLE = True
        request = HttpRequest()
        request.path = "/some-path/"
        response = self.middleware(request)
        self.get_response.assert_not_called()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, HTTP_503_SERVICE_UNAVAILABLE)
        content = json.loads(response.content)
        self.assertEqual(content["code"], "E0001")
        self.assertEqual(content["message"], "Server is under maintenance.")

    @override_settings(LANGUAGES=[("en", "English"), ("vi", "Vietnamese")])
    def test_get_allowed_paths(self) -> None:
        """Test that get_allowed_paths returns the correct list of allowed paths."""
        paths = self.middleware.get_allowed_paths()
        expected_paths = ["/admin", "/en/admin", "/vi/admin"]
        self.assertEqual(set(paths), set(expected_paths))

    def test_is_allowed_path(self) -> None:
        """Test is_allowed_path function for path classification."""
        self.middleware.allowed_paths = ["/admin", "/en/admin"]
        request = HttpRequest()

        request.path = "/admin/some/path"
        self.assertTrue(self.middleware.is_allowed_path(request))

        request.path = "/en/admin/some/path"
        self.assertTrue(self.middleware.is_allowed_path(request))

        request.path = "/some/other/path"
        self.assertFalse(self.middleware.is_allowed_path(request))
