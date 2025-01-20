import logging
from typing import Any, Dict, Optional

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http.response import JsonResponse

from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import set_rollback

from app.contrib.config import config
from app.contrib.error_code import ErrorCode

logger = logging.getLogger(__name__)


class APIExceptionHandler:
    """Exception handler for API exceptions.

    This handler converts exceptions into standardized JSON responses
    with appropriate HTTP status codes and error details.
    """

    def handle_exception(
        self, exc: Exception, _context: Dict[str, Any]
    ) -> Optional[Response]:
        """Handle main exception.

        Args:
            exc: The raised exception.
            _context: Context about the exception.

        Returns:
            A Response object with the error details, or None.

        """
        exc = self._normalize_exception(exc)

        if not isinstance(exc, exceptions.APIException):
            self._log_unexpected_error(exc)
            exc = InternalServerError()

        return self._handle_api_exception(exc)

    def _normalize_exception(self, exc: Exception) -> Exception:
        """Normalize exceptions to DRF Exception type.

        Args:
            exc: The raised exception.

        Returns:
            A normalized DRF exception.

        """
        if isinstance(exc, Http404):
            return exceptions.NotFound(*(exc.args))
        if isinstance(exc, PermissionDenied):
            return exceptions.PermissionDenied(*(exc.args))
        return exc

    def _handle_api_exception(self, exc: exceptions.APIException) -> Response:
        """Handle API Exceptions.

        Args:
            exc: The API exception.

        Returns:
            A Response object with the error details.

        """
        headers = self._get_exception_headers(exc)
        data = self._get_exception_data(exc)

        self._log_api_error(exc, data)
        set_rollback()

        response_class = Response if config.DEBUG else JsonResponse
        return response_class(data, status=exc.status_code, headers=headers)

    def _get_exception_headers(self, exc: exceptions.APIException) -> Dict[str, str]:
        """Get the headers for the exception response.

        Args:
            exc: The API exception.

        Returns:
            A dictionary of headers.

        """
        headers: Dict[str, str] = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = f"{int(exc.wait)}"
        return headers

    def _get_exception_data(self, exc: exceptions.APIException) -> Dict:
        """Get data for exception response.

        Args:
            exc: The API exception.

        Returns:
            A dictionary containing the error code and message.

        """
        if isinstance(exc, exceptions.ValidationError):
            exc = RequestBodyValidationError(exc.get_full_details())
        return exc.get_full_details()

    def _log_api_error(self, exc: exceptions.APIException, data: Dict) -> None:
        """Log details about API exceptions.

        Args:
            exc: The API exception.
            data: The error data.

        """
        logger.info(
            "API LOGGING: API exception: [%s: %s]",
            exc.__class__.__name__,
            data,
            exc_info=True,
        )

    def _log_unexpected_error(self, exc: Exception) -> None:
        """Log unexpected exceptions.

        Args:
            exc: The unexpected exception.

        """
        logger.exception(
            "API LOGGING: Unexpected exception occurred: [%s]",
            exc,
            exc_info=True,
        )


# Global exception handler function
exception_handler = APIExceptionHandler().handle_exception


class InternalServerError(exceptions.APIException):
    """Internal server error."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = ErrorCode.INTERNAL_SERVER_ERROR_DETAIL
    default_code = ErrorCode.INTERNAL_SERVER_ERROR_CODE


class ServiceUnavailable(exceptions.APIException):
    """Service Unavailable."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = ErrorCode.SERVICE_UNAVAILABLE_DETAIL
    default_code = ErrorCode.SERVICE_UNAVAILABLE_CODE


class RequestBodyValidationError(exceptions.ValidationError):
    """Request body validation error."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, detail: Dict[str, Any]) -> None:
        """Initialize the validation error with the detail.

        Args:
            detail: The validation error detail.

        """
        super().__init__(detail)
        self.detail = detail

    def get_full_details(self) -> Dict:
        """Get full details of the validation error.

        Returns:
            A dictionary containing the error code and message.

        """
        return {
            "code": self.default_code,
            "message": self.detail,
        }
