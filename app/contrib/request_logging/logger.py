from functools import lru_cache
from typing import Any, Dict

from django.http import HttpRequest

from app.contrib.constants import LoggerConstant


class RequestBodyLogger:
    """Process and log request bodies efficiently."""

    @classmethod
    @lru_cache(maxsize=100)
    def get_content_type(cls, content_type: str) -> str:
        """Cache content type parsing.

        Args:
            content_type: The content type string.

        Returns:
            The parsed content type (lowercase, without parameters).

        """
        return content_type.split(";")[0].lower()

    @classmethod
    def should_log_body(cls, request: HttpRequest) -> bool:
        """Check whether the request body should be logged.

        Args:
            request: The HttpRequest object.

        Returns:
            True if the request body should be logged, False otherwise.

        """
        content_type = cls.get_content_type(request.content_type)
        return content_type in {"application/json", "application/x-www-form-urlencoded"}

    @classmethod
    def sanitize_body(cls, body: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from body.

        Args:
            body: The request body dictionary.

        Returns:
            A sanitized copy of the body with sensitive fields masked.

        """
        sanitized = body.copy()
        for key in LoggerConstant.SENSITIVE_FIELDS & set(sanitized.keys()):
            sanitized[key] = "***"
        return sanitized
