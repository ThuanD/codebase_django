from rest_framework import serializers


class ErrorSerializer(serializers.Serializer):
    """Serializer for error responses."""

    code = serializers.CharField()
    message = serializers.CharField()


class ValidationErrorSerializer(serializers.Serializer):
    """Serializer for validation errors."""

    code = serializers.CharField()
    message = serializers.DictField()
