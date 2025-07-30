from django.urls import path

from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

app_name = "apidocs"
urlpatterns = [
    path("redoc/", SpectacularRedocView.as_view(url_name="apidocs:schema"), name="redoc"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="apidocs:schema"),
        name="swagger-ui",
    ),
    path(
        "schema/",
        SpectacularJSONAPIView.as_view(),
        name="schema",
    ),
]
