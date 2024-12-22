from django.utils import timezone
from rest_framework import serializers


class ErrorSerializer(serializers.Serializer):
    """Serializer for error responses."""

    code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField(default=timezone.now)
    request_id = serializers.CharField(required=False)
