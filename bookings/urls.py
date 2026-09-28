from django.urls import path
from .views import BookingStatusUpdateView

from .views import (
    BookingListCreateView,
    BookingDetailView,
    BookingCancelView,
)

urlpatterns = [
    path("", BookingListCreateView.as_view(), name="booking-list-create"),
    path("<int:pk>/", BookingDetailView.as_view(), name="booking-detail"),
    path("<int:pk>/cancel/", BookingCancelView.as_view(), name="booking-cancel"),
    path(
    "<int:pk>/status/",
    BookingStatusUpdateView.as_view(),
    name="booking-status"
),
]