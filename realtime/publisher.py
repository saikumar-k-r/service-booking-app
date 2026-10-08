from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .events import BOOKING_STATUS_CHANGED


def publish_booking_status(user_id, booking_id, status):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "realtime_event",
            "event_id": f"booking-{booking_id}-{status}",
            "event": BOOKING_STATUS_CHANGED,
            "payload": {
                "booking_id": booking_id,
                "status": status,
            },
        },
    )