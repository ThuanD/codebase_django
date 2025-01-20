from rest_framework import serializers


class ErrorSerializer(serializers.Serializer):
    """Serializer for error responses.

    Used to define the structure of error responses in the API documentation.
    """

    code = serializers.CharField(help_text="Error code")
    message = serializers.CharField(help_text="Error message")


class ValidationErrorSerializer(serializers.Serializer):
    """Serializer for validation errors.

    Used to define the structure of validation error responses in the API documentation.
    """

    code = serializers.CharField(help_text="Error code")
    message = serializers.DictField(help_text="Validation error messages per field")
