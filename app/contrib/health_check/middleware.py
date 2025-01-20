from http import HTTPStatus
from typing import Callable

from django.core.cache import cache
from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse

from app.contrib.config import config
from app.contrib.constants import CacheKey
from app.contrib.exception import ServiceUnavailable
from app.contrib.health_check.throttling import HealthCheckThrottle


class HealthCheckMiddleware:
    """Health check middleware."""

    def __init__(self, get_response: Callable) -> None:
        """Initialize the middleware."""
        self.get_response = get_response
        self.health_check_path = config.HEALTH_CHECK_ENDPOINT
        self.throttle = HealthCheckThrottle()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request.

        Args:
            request: The incoming HTTP request.

        Returns:
            HTTP response, either the health check response
            or the next middleware's response.

        """
        if request.path == self.health_check_path:
            if not self.throttle.allow_request(request, None):
                return HttpResponse(status=HTTPStatus.TOO_MANY_REQUESTS)
            return self.health_check(request)
        return self.get_response(request)

    def health_check(self, _request: HttpRequest) -> HttpResponse:
        """Perform health checks and return an HTTP response.

        Args:
            _request: The incoming HTTP request.

        Returns:
            HTTP response indicating the health status.

        """
        # Check database connectivity
        try:
            connection.ensure_connection()
        except Exception as e:
            exception = ServiceUnavailable(detail=f"database unavailable: {e}")
            return JsonResponse(
                exception.get_full_details(), status=exception.status_code
            )

        # Check cache connectivity (using the default cache)
        try:
            cache.set(CacheKey.HEALTH_CHECK_KEY, CacheKey.HEALTH_CHECK_VALUE, timeout=5)
            if cache.get(CacheKey.HEALTH_CHECK_KEY) != CacheKey.HEALTH_CHECK_VALUE:
                raise ValueError("Cache did not return expected value")
        except Exception as e:
            exception = ServiceUnavailable(detail=f"cache unavailable: {e}")
            return JsonResponse(
                exception.get_full_details(), status=exception.status_code
            )

        return HttpResponse(status=HTTPStatus.OK)


class MaintenanceMiddleware:
    """Middleware that puts the site into maintenance mode."""

    def __init__(self, get_response: Callable) -> None:
        """Initialize the middleware."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process each request to determine if maintenance mode is active.

        Args:
            request: The incoming HTTP request.

        Returns:
            HTTP response, either the regular response or the maintenance response.

        """
        if not config.MAINTENANCE_ENABLE:
            return self.get_response(request)

        # Allow staff to bypass maintenance mode.
        if hasattr(request, "user") and request.user.is_staff:
            return self.get_response(request)

        # Allow access to specific URLs (e.g., admin, login, a specific API endpoint).
        if any(request.path.startswith(url) for url in config.MAINTENANCE_ALLOWED_URLS):
            return self.get_response(request)

        # Allow access from specific IP addresses.
        if request.META.get("REMOTE_ADDR") in config.MAINTENANCE_ALLOWED_IPS:
            return self.get_response(request)

        # Return a 503 Service Unavailable response with a custom message.
        exception = ServiceUnavailable(detail=config.MAINTENANCE_MESSAGE)
        return JsonResponse(exception.get_full_details(), status=exception.status_code)
