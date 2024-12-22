import json
import unittest
from unittest.mock import Mock, patch

from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory
from rest_framework.status import HTTP_200_OK

from app.contrib.request_logging.middleware import RequestLoggingMiddleware
from app.message.middlewares import END_REQUEST, START_REQUEST


class TestRequestLoggingMiddleware(unittest.TestCase):
    """Test the RequestLoggingMiddleware class."""

    def setUp(self) -> None:
        """Set up the test environment."""
        self.factory = RequestFactory()
        self.middleware = RequestLoggingMiddleware(
            get_response=Mock(return_value=HttpResponse())
        )

    def tearDown(self) -> None:
        """Tear down the test environment."""
        cache.clear()

    @patch("app.contrib.request_logging.middleware.logger")
    def test_middleware_call(self, mock_logger: Mock) -> None:
        """Test the middleware call."""
        request = self.factory.post("/test/", {"param": "value"})
        request.id = "123456"
        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTP_200_OK)

    @patch("app.contrib.request_logging.middleware.logger")
    def test_log_request(self, mock_logger: Mock) -> None:
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
    def test_log_request_with_body(self, mock_logger: Mock) -> None:
        """Test logging a request with a body."""
        data = {"param": "value"}
        request = self.factory.post(
            "/test/",
            data=data,
            content_type="application/json",
        )
        request.id = "123456"
        RequestLoggingMiddleware.log_request(request, END_REQUEST)

        expected_log = (
            '[request_id=123456, method=POST, content_type=application/json, '
            f'path=/test/, query=, body={json.dumps(data)}, user_agent=None, '
            f'ip=127.0.0.1], '
            f"End of request."
        )
        mock_logger.info.assert_called_once_with(expected_log)
