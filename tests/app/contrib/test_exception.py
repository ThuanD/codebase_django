import json
from unittest import TestCase

from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.test import override_settings

from rest_framework import exceptions, status
from rest_framework.response import Response

from app.contrib.config import config
from app.contrib.error_code import ErrorCode
from app.contrib.exception import APIExceptionHandler, exception_handler


class TestExceptionHandler(TestCase):
    """Test the exception handler."""

    def tearDown(self):
        """Reset the config to the default values."""
        config.reset()

    def test_http404_exception(self):
        """Test the HTTP 404 exception."""
        response = exception_handler(Http404(), {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        content = json.loads(response.content)
        self.assertEqual(content["code"], "not_found")
        self.assertEqual(content["message"], "Not found.")

    def test_permission_denied_exception(self):
        """Test the permission denied exception."""
        response = exception_handler(PermissionDenied(), {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        content = json.loads(response.content)
        self.assertEqual(content["code"], "permission_denied")
        self.assertEqual(content["message"], "You do not have permission to perform this action.")

    def test_api_exception_with_auth_header(self):
        """Test the API exception with an authentication header."""
        exc = exceptions.AuthenticationFailed()
        exc.auth_header = "Bearer realm='api'"
        response = exception_handler(exc, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        content = json.loads(response.content)
        self.assertEqual(content["code"], "authentication_failed")
        self.assertEqual(content["message"], "Incorrect authentication credentials.")
        self.assertEqual(response["WWW-Authenticate"], "Bearer realm='api'")

    def test_api_exception_with_wait(self):
        """Test the API exception with a wait time."""
        exc = exceptions.Throttled(wait=60)
        response = exception_handler(exc, {})
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response["Retry-After"], "60")

    def test_validation_error(self):
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
    def test_json_response_in_production(self):
        """Test the JSON response in production."""
        response = exception_handler(exceptions.NotFound(), {})
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(DEBUG=True)
    def test_response_in_development(self):
        """Test the response in development."""
        res = exception_handler(exceptions.NotFound(), {})
        self.assertIsInstance(res, Response)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_handle_unexpected_exception(self):
        """Test handling of unexpected exceptions."""
        # Create an unexpected exception
        unexpected_exception = Exception("This is an unexpected error.")

        # Call the handler with the unexpected exception
        response = APIExceptionHandler().handle_exception(unexpected_exception, {})

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        content = json.loads(response.content)
        self.assertEqual(content["code"], ErrorCode.INTERNAL_SERVER_ERROR_CODE)
        self.assertEqual(content["message"], ErrorCode.INTERNAL_SERVER_ERROR_DETAIL)
