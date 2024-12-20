import json
import logging
import uuid
from typing import Callable, Optional

from django.http import HttpRequest, HttpResponse

from app.contrib.request_logging.logger import RequestBodyLogger
from app.message.middlewares import END_REQUEST, START_REQUEST

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Middleware for logging request/response."""

    def __init__(self, get_response: Callable) -> None:
        """Initialize the middleware with the get_response function."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Handle the request and response cycle."""
        request.id = str(uuid.uuid4())

        if RequestBodyLogger.should_log_body(request):
            self.log_request(request, START_REQUEST)

        response = self.get_response(request)

        if RequestBodyLogger.should_log_body(request):
            self.log_request(request, END_REQUEST)

        return response

    @staticmethod
    def get_request_body(request: HttpRequest) -> Optional[str]:
        """Get the request body if it should be logged."""
        if not RequestBodyLogger.should_log_body(request):
            return None

        if request.content_type == "application/x-www-form-urlencoded":
            body = request.POST.dict()
        else:
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                logger.warning("API LOGGING: Failed to decode request body.")
                return None
            except Exception as error:
                logger.warning(
                    "API LOGGING: Failed to process request body: %s",
                    error)
                return None

        if len(str(body)) > RequestBodyLogger.MAX_BODY_SIZE:
            return "BODY TOO LARGE"
        return json.dumps(RequestBodyLogger.sanitize_body(body))

    @staticmethod
    def log_request(request: HttpRequest, stage: str) -> None:
        """Log the request with the given count and stage."""
        query = request.META.get("QUERY_STRING", "")
        body = RequestLoggingMiddleware.get_request_body(request)
        log_message = (
            f"[request_id={request.id}, "
            f"method={request.method}, "
            f"content_type={request.content_type}, "
            f"path={request.path}, "
            f"query={query}, "
            f"body={body}, "
            f"user_agent={request.META.get('HTTP_USER_AGENT')}, "
            f"ip={request.META.get('REMOTE_ADDR')}], {stage}"
        )
        logger.info(log_message)
