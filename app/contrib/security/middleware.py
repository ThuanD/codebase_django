from http import HTTPStatus
from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse


class SecurityHeadersMiddleware:
    """Middleware to add security headers to all responses."""

    def __init__(self, get_response: Callable) -> None:
        """Initialize the middleware."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Add security headers to the response."""
        response = self.get_response(request)

        # Ignore debug mode
        exempted_debug_codes = (
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.NOT_FOUND,
        )
        if response.status_code in exempted_debug_codes and settings.DEBUG:
            return response

        # Prevent clickjacking attacks
        response["X-Frame-Options"] = "DENY"

        # Enable browser XSS filtering
        response["X-XSS-Protection"] = "1; mode=block"

        # Prevent MIME type sniffing
        response["X-Content-Type-Options"] = "nosniff"

        # HSTS (HTTP Strict Transport Security)
        response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy
        response["Content-Security-Policy"] = self._get_csp_policy()

        return response

    def _get_csp_policy(self) -> str:
        """Generate Content Security Policy."""
        return "; ".join(
            [
                "default-src 'self'",
                "img-src 'self' data: https:",
                "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net ",
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
                "frame-ancestors 'none'",
            ]
        )
