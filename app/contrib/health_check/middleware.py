from http import HTTPStatus
from typing import Callable, List

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from app.contrib.config import config
from app.contrib.constants import HEALTH_CHECK_API
from app.contrib.exception import ServiceUnavailable
from app.contrib.health_check.throttling import HealthCheckThrottle


class HealthCheckMiddleware:
    """Health check middleware for operators."""

    def __init__(self, get_response: Callable) -> None:
        """Initialize the middleware with the get_response function."""
        self.get_response = get_response
        self.throttle = HealthCheckThrottle()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Handle the request and response cycle."""
        if request.path == HEALTH_CHECK_API:
            if not self.throttle.allow_request(request, None):
                return HttpResponse(status=HTTPStatus.TOO_MANY_REQUESTS)
            return HttpResponse(status=HTTPStatus.OK)
        return self.get_response(request)


class MaintenanceMiddleware:
    """Maintenance middleware for users."""

    def __init__(self, get_response: Callable) -> None:
        """Initialize the middleware with the get_response function."""
        self.get_response = get_response
        self.allowed_paths: List[str] = self.get_allowed_paths()

    @staticmethod
    def get_allowed_paths() -> List[str]:
        """Get the allowed paths for maintenance mode."""
        allowed_paths = ["/admin"]
        allowed_paths += [f"/{lang[0]}/admin" for lang in settings.LANGUAGES]
        return allowed_paths

    def is_allowed_path(self, request: HttpRequest) -> bool:
        """Check if the request path is allowed in maintenance mode."""
        return any(request.path.startswith(path) for path in self.allowed_paths)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Handle the request and response cycle."""
        if self.is_allowed_path(request) or not config.MAINTENANCE_ENABLE:
            return self.get_response(request)
        return JsonResponse(
            ServiceUnavailable().get_full_details(),
            status=ServiceUnavailable.status_code,
        )
