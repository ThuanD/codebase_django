# Endpoint to health check API service
HEALTH_CHECK_API = "/api/health_check/"

TRUE_VALUES = ["1", "t", "true", "True", "TRUE", "y", "yes", "Yes", "YES"]


class Pagination:
    """Class for pagination constants."""

    MAX_PAGE_SIZE = 100
    PAGE_SIZE_QUERY_PARAM = "page_size"
