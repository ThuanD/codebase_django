from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample

from app.contrib.exception import RequestBodyValidationError

ERROR_REQUEST_BODY_DESCRIPTION = _(
    "Check the request body schema to see the validation information for the fields. "
    "Error `message` are mutable."
)


class RequestBodyValidationErrorExample(OpenApiExample):
    """Example for the request body validation error."""

    def __init__(self) -> None:
        """Initialize the example."""
        super().__init__(
            name="RequestBodyValidationError",
            description=ERROR_REQUEST_BODY_DESCRIPTION,
            value=RequestBodyValidationError(
                {
                    "field": [
                        {
                            "message": _("Error message for this field!"),
                            "code": "invalid",
                        }
                    ]
                }
            ).get_full_details(),
        )
