from django.utils.translation import gettext_lazy as _


class ErrorCode:
    """Error code."""

    UNEXPECTED_ERROR_CODE = "E0000"
    UNEXPECTED_ERROR_DETAIL = _("Unexpected error.")

    MAINTENANCE_ERROR_CODE = "E0001"
    MAINTENANCE_ERROR_DETAIL = _("Server is under maintenance.")
