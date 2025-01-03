from django.utils.translation import gettext_lazy as _


class ErrorCode:
    """Error code."""

    INTERNAL_SERVER_ERROR_CODE = "E0000"
    INTERNAL_SERVER_ERROR_DETAIL = _("Internal Server Error.")

    SERVICE_UNAVAILABLE_CODE = "E0001"
    SERVICE_UNAVAILABLE_DETAIL = _("Service Unavailable.")
