import json
import unittest
from unittest.mock import Mock, patch

from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory

from rest_framework.status import HTTP_200_OK

from app.constants import LoggerConstant
from app.contrib.request_logging.middleware import RequestLoggingMiddleware
from app.message.middlewares import START_REQUEST


class TestRequestLoggingMiddleware(unittest.TestCase):
    """Test the RequestLoggingMiddleware class."""

    def setUp(self):
        """Set up the test environment."""
        self.factory = RequestFactory()
        self.middleware = RequestLoggingMiddleware(
            get_response=Mock(return_value=HttpResponse())
        )

    def tearDown(self):
        """Tear down the test environment."""
        cache.clear()

    def test_middleware_call(self):
        """Test the middleware call."""
        request = self.factory.post("/test/", {"param": "value"})
        request.id = "123456"
        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTP_200_OK)

    @patch("app.contrib.request_logging.middleware.logger")
    def test_log_request(self, mock_logger: Mock):
        """Test logging a request."""
        request = self.factory.get("/test/", {"param": "value"})
        request.id = "123456"
        RequestLoggingMiddleware.log_request(request, START_REQUEST)

        expected_log = (
            "[request_id=123456, method=GET, content_type=, path=/test/, "
            "query=param=value, body=None, user_agent=None, ip=127.0.0.1],"
            " Start of request."
        )
        mock_logger.info.assert_called_once_with(expected_log)

    @patch("app.contrib.request_logging.middleware.logger")
    def test_log_request_with_sensitive_data(self, mock_logger: Mock):
        """Test logging a request with sensitive data."""
        data = {"password": "value"}
        data_log = {"password": "***"}
        request = self.factory.post(
            "/test/",
            data,
            content_type="application/json",
        )
        request.id = "123456"
        RequestLoggingMiddleware.log_request(request, START_REQUEST)

        expected_log = (
            "[request_id=123456, method=POST, content_type=application/json, "
            f"path=/test/, query=, body={json.dumps(data_log)}, user_agent=None, "
            "ip=127.0.0.1], "
            "Start of request."
        )
        mock_logger.info.assert_called_once_with(expected_log)

    @patch("app.contrib.request_logging.middleware.logger")
    def test_log_request_with_body(self, mock_logger: Mock):
        """Test logging a request with a body."""
        data = {"param": "value"}
        request = self.factory.post(
            "/test/",
            data=data,
            content_type="application/json",
        )
        self.middleware(request)
        log_message = mock_logger.info.call_args[0][0]

        self.assertIn("method=POST", log_message)
        self.assertIn("content_type=application/json", log_message)
        self.assertIn("path=/test/", log_message)
        self.assertIn("query=", log_message)
        self.assertIn(f"body={json.dumps(data)}", log_message)

    @patch("app.contrib.request_logging.middleware.logger")
    def test_call_does_not_log_when_not_required(self, mock_logger: Mock):
        """Test middleware skips logging when body should not be logged."""
        request = self.factory.post(
            "/test/",
            data="data",
            content_type="text/plain",
        )
        response = self.middleware(request)

        self.assertIsInstance(response, HttpResponse)
        mock_logger.assert_not_called()

    @patch("app.contrib.request_logging.middleware.logger")
    def test_log_request_content_type_form_urlencoded(self, _: Mock):
        """Test logging a request with content type form urlencoded."""
        data = b"data=value"
        data_json = {"data": "value"}
        request = self.factory.post(
            "/test/",
            data=data,
            content_type="application/x-www-form-urlencoded",
        )

        body = RequestLoggingMiddleware.get_request_body(request)

        self.assertEqual(body, json.dumps(data_json))

    @patch("app.contrib.request_logging.middleware.logger")
    def test_application_json_encode_error(self, mock_logger: Mock):
        """Test logging a request with application json encode error."""
        request = self.factory.post(
            "/test/", data="invalid_json", content_type="application/json"
        )

        body = RequestLoggingMiddleware.get_request_body(request)

        self.assertIsNone(body)
        mock_logger.warning.assert_called_once_with(
            "API LOGGING: Failed to decode request body."
        )

    @patch("app.contrib.request_logging.middleware.logger")
    def test_application_json_encode_unknown_error(self, mock_logger: Mock):
        """Test logging a request with application json encode unknown error."""
        request = self.factory.post(
            "/test/", data=b"\xff\xff", content_type="application/json"
        )

        body = RequestLoggingMiddleware.get_request_body(request)

        self.assertIsNone(body)
        log_message = mock_logger.warning.call_args[0][0]
        self.assertIn("Failed to process request body", log_message)

    @patch.object(LoggerConstant, "MAX_BODY_SIZE", 1)
    def test_logs_body_max_size_exceed(self):
        """Test logging a request with body max size exceed."""
        data = {"param": "value"}
        request = self.factory.post(
            "/test/",
            data=data,
            content_type="application/json",
        )
        body = RequestLoggingMiddleware.get_request_body(request)

        self.assertEqual(body, "BODY TOO LARGE")
