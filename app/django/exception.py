import logging
from typing import Any, Dict, Optional

from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse

from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
)
from rest_framework.views import set_rollback

from app.config import config
from app.message.errors import ErrorCode

logger = logging.getLogger(__name__)


class APIExceptionHandler:
    """Exception handler for API exceptions."""

    def handle_exception(self, exc: Exception, _: Dict[str, Any]) -> Optional[Response]:
        """Handle main exception."""
        exc = self._normalize_exception(exc)

        if not isinstance(exc, exceptions.APIException):
            self._log_unexpected_error(exc)
            exc = UnexpectedError()
        return self._handle_api_exception(exc)

    def _normalize_exception(self, exc: Exception) -> Exception:
        """Normalize exceptions to DRF Exception type."""
        if isinstance(exc, Http404):
            return exceptions.NotFound(*(exc.args))
        if isinstance(exc, PermissionDenied):
            return exceptions.PermissionDenied(*(exc.args))
        return exc

    def _handle_api_exception(self, exc: exceptions.APIException) -> Response:
        """Handle API Exceptions."""
        headers = self._get_exception_headers(exc)
        data = self._get_exception_data(exc)

        self._log_api_error(exc, data)
        set_rollback()

        response_class = Response if config.DEBUG else JsonResponse
        return response_class(data, status=exc.status_code, headers=headers)

    def _get_exception_headers(self, exc: exceptions.APIException) -> Dict[str, str]:
        """Get the headers for the exception response."""
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header  # noqa
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait  # noqa
        return headers

    def _get_exception_data(self, exc: exceptions.APIException) -> Dict:
        """Get data for exception response."""
        if isinstance(exc, exceptions.ValidationError):
            exc = RequestBodyValidationError(exc.get_full_details())
        return exc.get_full_details()

    def _log_api_error(self, exc: exceptions.APIException, data: Dict) -> None:
        """Log details about API exceptions."""
        logger.info(
            "API LOGGING: API exception: [%s: %s]",
            exc.__class__.__name__,
            data,
            exc_info=True,
        )

    def _log_unexpected_error(self, exc: Exception) -> None:
        """Log unexpected exceptions."""
        logger.exception(
            "API LOGGING: Unexpected exception occurred: [{%s}]", exc, exc_info=True
        )


# Global exception handler function
exception_handler = APIExceptionHandler().handle_exception


class UnexpectedError(exceptions.APIException):
    """Unexpected error."""

    status_code = HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = ErrorCode.UNEXPECTED_ERROR_DETAIL
    default_code = ErrorCode.UNEXPECTED_ERROR_CODE


class RequestBodyValidationError(exceptions.ValidationError):
    """Request body validation error."""

    def __init__(self, detail: Dict[str, Any]) -> None:
        """Initialize the validation error with the detail."""
        self.detail = detail

    def get_full_details(self) -> Dict:
        """Get full details of the validation error."""
        return {
            "code": self.default_code,
            "message": self.detail,
        }


class ServerIsUnderMaintenance(exceptions.APIException):
    """Server is under maintenance."""

    status_code = HTTP_503_SERVICE_UNAVAILABLE
    default_detail = ErrorCode.MAINTENANCE_ERROR_DETAIL
    default_code = ErrorCode.MAINTENANCE_ERROR_CODE
