import unittest

from django.urls import resolve, reverse

from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


class TestAPIDocURLs(unittest.TestCase):
    """Test suite for API documentation URLs."""

    def test_redoc_url(self) -> None:
        """Test the redoc URL."""
        url = reverse("api_doc:redoc")
        self.assertEqual(url, "/api_doc/redoc/")
        view = resolve(url)
        self.assertEqual(view.func.view_class, SpectacularRedocView)

    def test_swagger_url(self) -> None:
        """Test the swagger URL."""
        url = reverse("api_doc:swagger-ui")
        self.assertEqual(url, "/api_doc/swagger/")
        view = resolve(url)
        self.assertEqual(view.func.view_class, SpectacularSwaggerView)

    def test_schema_url(self) -> None:
        """Test the schema URL."""
        url = reverse("api_doc:schema")
        self.assertEqual(url, "/api_doc/schema/")
        view = resolve(url)
        self.assertEqual(view.func.view_class, SpectacularJSONAPIView)
