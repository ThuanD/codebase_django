import unittest
from http import HTTPStatus
from unittest.mock import Mock

from django.http import HttpResponse
from django.test import RequestFactory
from django.test.utils import override_settings

from app.contrib.security.middleware import SecurityHeadersMiddleware


class TestSecurityHeadersMiddleware(unittest.TestCase):
    """Test the SecurityHeadersMiddleware class."""

    def setUp(self):
        """Set up the test environment."""
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(get_response=Mock(return_value=HttpResponse()))

    @override_settings(DEBUG=False)
    def test_add_security_headers(self):
        """Test that security headers are added to the response."""
        request = self.factory.get("/test/")
        response = self.middleware(request)

        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertEqual(response["X-XSS-Protection"], "1; mode=block")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(
            response["Strict-Transport-Security"], "max-age=31536000; includeSubDomains"
        )
        self.assertIn("Content-Security-Policy", response)

    @override_settings(DEBUG=True)
    def test_exempted_status_codes_in_debug_mode(self):
        """Test that headers are not added in debug mode for exempted status codes."""
        request = self.factory.get("/test/")
        response = HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)
        self.middleware.get_response = Mock(return_value=response)

        response = self.middleware(request)

        self.assertNotIn("X-Frame-Options", response)
        self.assertNotIn("X-XSS-Protection", response)

    def test_get_csp_policy(self):
        """Test the Content Security Policy generation."""
        expected_policy = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net ; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "frame-ancestors 'none'"
        )
        self.assertEqual(self.middleware._get_csp_policy(), expected_policy)
