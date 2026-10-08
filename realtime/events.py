import uuid

BOOKING_STATUS_CHANGED = "booking.status_changed"
PRESENCE_CHANGED = "presence.changed"
HEARTBEAT = "heartbeat"
HEARTBEAT_ACK = "heartbeat.ack"


def build_event(event, payload):
    return {
        "event_id": str(uuid.uuid4()),
        "event": event,
        "payload": payload,
    }