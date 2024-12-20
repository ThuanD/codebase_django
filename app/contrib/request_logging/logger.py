from functools import lru_cache
from typing import Any, Dict

from django.http import HttpRequest


class RequestBodyLogger:
    """Process and log request bodies efficiently."""

    MAX_BODY_SIZE = 1024 * 10  # 10KB
    SENSITIVE_FIELDS = {"password", "token", "secret"}

    @classmethod
    @lru_cache(maxsize=100)
    def get_content_type(cls, content_type: str) -> str:
        """Cache content type parsing."""
        return content_type.split(";")[0].lower()

    @classmethod
    def should_log_body(cls, request: HttpRequest) -> bool:
        """Check whether the request body should be logged."""
        content_type = cls.get_content_type(request.content_type)
        return content_type in {"application/json", "application/x-www-form-urlencoded"}

    @classmethod
    def sanitize_body(cls, body: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from body."""
        sanitized = body.copy()
        for key in cls.SENSITIVE_FIELDS & set(sanitized.keys()):
            sanitized[key] = "***"
        return sanitized
