from rest_framework.pagination import PageNumberPagination

from app.constants import Pagination


class CustomPagination(PageNumberPagination):
    """Custom pagination class for API responses.

    This class extends DRF's PageNumberPagination to provide customized
    pagination with configurable page sizes and maximum limits.

    Attributes:
        max_page_size (int): Maximum number of items per page
        page_size_query_param (str): Query parameter name for page size
    """

    max_page_size = Pagination.MAX_PAGE_SIZE
    page_size_query_param = Pagination.PAGE_SIZE_QUERY_PARAM
