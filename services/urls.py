from django.urls import path

from .views import (
    ServiceListCreateView,
    ServiceDetailView,ServiceImageListCreateView,
    ServiceImageDeleteView,
)

urlpatterns = [
    path(
        "",
        ServiceListCreateView.as_view(),
        name="service-list-create"
    ),

    path(
        "<int:pk>/",
        ServiceDetailView.as_view(),
        name="service-detail"
    ),
    path(
    "<int:service_id>/images/",
    ServiceImageListCreateView.as_view(),
    name="service-images"
),
path(
    "<int:service_id>/images/<int:pk>/",
    ServiceImageDeleteView.as_view(),
    name="service-image-delete"
),
]