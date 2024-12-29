from typing import Callable

from django.http import HttpRequest
from django.http.response import HttpResponseBase

from rest_framework.throttling import AnonRateThrottle


class HealthCheckThrottle(AnonRateThrottle):
    """Rate limiting for health check endpoint."""

    rate = "60/minute"  # Limit 60 requests/minute

    def get_cache_key(
        self, request: HttpRequest, _: Callable[..., HttpResponseBase]
    ) -> str:
        """Generate unique cache key for request."""
        return f"health_check_throttle_{request.META.get('REMOTE_ADDR', '')}"
