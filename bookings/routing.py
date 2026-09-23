from django.urls import re_path
from .consumers import BookingStatusConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/bookings/(?P<booking_id>\d+)/$",
        BookingStatusConsumer.as_asgi()
    ),
]