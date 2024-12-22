from typing import Optional

from django.core.cache import cache
from django.http import HttpRequest

from rest_framework.throttling import SimpleRateThrottle


class CustomIPRateThrottle(SimpleRateThrottle):
    """Rate limiting based on IP address with burst control.

    Attributes:
        rate: Default rate limit
        burst_rate: Higher rate allowed for short periods
        burst_duration: Duration in seconds for burst allowance

    """

    rate = "100/hour"  # Default rate
    burst_rate = "200/hour"  # Burst allowance
    burst_duration = 300  # 5 minutes

    def get_cache_key(self, request: HttpRequest, _: Optional[object]) -> str:
        """Generate unique cache key for request."""
        ident = self.get_ident(request)
        return f"throttle_ip_{ident}"

    def allow_request(self, request: HttpRequest, view: Optional[object]) -> bool:
        """Check if request should be allowed with burst consideration."""
        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)

        # Check burst period
        if self._is_burst_period():
            self.rate = self.burst_rate

        return super().allow_request(request, view)

    def _is_burst_period(self) -> bool:
        """Determine if current time is within burst period."""
        burst_key = f"{self.key}_burst"
        if not cache.get(burst_key):
            cache.set(burst_key, True, self.burst_duration)
            return True
        return False
