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
        url = reverse("apidocs:redoc")
        self.assertEqual(url, "/apidocs/redoc/")
        view = resolve(url)
        self.assertEqual(view.func.view_class, SpectacularRedocView)

    def test_swagger_url(self) -> None:
        """Test the swagger URL."""
        url = reverse("apidocs:swagger-ui")
        self.assertEqual(url, "/apidocs/swagger/")
        view = resolve(url)
        self.assertEqual(view.func.view_class, SpectacularSwaggerView)

    def test_schema_url(self) -> None:
        """Test the schema URL."""
        url = reverse("apidocs:schema")
        self.assertEqual(url, "/apidocs/schema/")
        view = resolve(url)
        self.assertEqual(view.func.view_class, SpectacularJSONAPIView)
