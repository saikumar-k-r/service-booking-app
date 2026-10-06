from django.urls import path

from .views import ExternalServiceCheckView


urlpatterns = [
    path(
        "external/check/",
        ExternalServiceCheckView.as_view(),
        name="external-service-check",
    ),
]
