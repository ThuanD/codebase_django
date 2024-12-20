import json
from unittest import TestCase

from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.test import override_settings
from rest_framework import exceptions, response, status

from app.config import config
from app.django.exception import exception_handler


class TestExceptionHandler(TestCase):
    """Test the exception handler."""

    def tearDown(self) -> None:
        """Reset the config to the default values."""
        config.reset()

    def test_http404_exception(self) -> None:
        """Test the HTTP 404 exception."""
        response = exception_handler(Http404(), {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        content = json.loads(response.content)
        self.assertEqual(content["code"], "not_found")
        self.assertEqual(content["message"], "Not found.")

    def test_permission_denied_exception(self) -> None:
        """Test the permission denied exception."""
        response = exception_handler(PermissionDenied(), {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        content = json.loads(response.content)
        self.assertEqual(content["code"], "permission_denied")
        self.assertEqual(
            content["message"], "You do not have permission to perform this action."
        )

    def test_api_exception_with_auth_header(self) -> None:
        """Test the API exception with an authentication header."""
        exc = exceptions.AuthenticationFailed()
        exc.auth_header = "Bearer realm='api'"
        response = exception_handler(exc, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        content = json.loads(response.content)
        self.assertEqual(content["code"], "authentication_failed")
        self.assertEqual(content["message"], "Incorrect authentication credentials.")
        self.assertEqual(response["WWW-Authenticate"], "Bearer realm='api'")

    def test_api_exception_with_wait(self) -> None:
        """Test the API exception with a wait time."""
        exc = exceptions.Throttled(wait=60)
        response = exception_handler(exc, {})
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response["Retry-After"], "60")

    def test_validation_error(self) -> None:
        """Test the validation error."""
        exc = exceptions.ValidationError({"field": ["This field is required."]})
        response = exception_handler(exc, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        content = json.loads(response.content)
        self.assertEqual(content["code"], "invalid")
        self.assertEqual(
            content["message"],
            {"field": [{"message": "This field is required.", "code": "invalid"}]},
        )

    @override_settings(DEBUG=False)
    def test_json_response_in_production(self) -> None:
        """Test the JSON response in production."""
        response = exception_handler(exceptions.NotFound(), {})
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(DEBUG=True)
    def test_response_in_development(self) -> None:
        """Test the response in development."""
        res = exception_handler(exceptions.NotFound(), {})
        self.assertIsInstance(res, response.Response)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
