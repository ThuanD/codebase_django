import re
from typing import Optional

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class InputValidator:
    """Utility class for validating user input.

    Provides methods for common validation scenarios with
    configurable rules and sanitization.
    """

    # Regex patterns for validation
    PATTERNS = {
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "username": r"^[a-zA-Z0-9_]{3,30}$",
        "phone": r"^\+?1?\d{9,15}$",
    }

    # Characters to escape in user input
    ESCAPE_CHARS = ["<", ">", "&", '"', "'", "`"]

    @classmethod
    def validate_string(
        cls,
        value: str,
        min_length: int = 1,
        max_length: int = 255,
        pattern: Optional[str] = None,
    ) -> str:
        """Validate and sanitize string input.

        Args:
            value: Input string to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            pattern: Optional regex pattern to match

        Returns:
            Sanitized string value

        Raises:
            ValidationError: If validation fails

        """
        if not isinstance(value, str):
            raise ValidationError(_("Value must be a string"))

        value = cls.sanitize_string(value)

        if len(value) < min_length:
            raise ValidationError(
                _("Value must be at least %(min)d characters long"),
                params={"min": min_length},
            )

        if len(value) > max_length:
            raise ValidationError(
                _("Value must be at most %(max)d characters long"),
                params={"max": max_length},
            )

        if pattern and not re.match(pattern, value):
            raise ValidationError(_("Value format is invalid"))

        return value

    @classmethod
    def sanitize_string(cls, value: str) -> str:
        """Sanitize string by escaping special characters."""
        for char in cls.ESCAPE_CHARS:
            value = value.replace(char, f"&{char};")
        return value.strip()
