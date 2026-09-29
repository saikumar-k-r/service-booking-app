from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Booking


VALID_TRANSITIONS = {
    "PENDING": {
        "CONFIRMED",
        "CANCELLED",
        "PAYMENT_FAILED",
    },
    "CONFIRMED": {
        "IN_PROGRESS",
        "CANCELLED",
    },
    "IN_PROGRESS": {
        "COMPLETED",
    },
    "COMPLETED": set(),
    "CANCELLED": set(),
    "PAYMENT_FAILED": set(),
}


def validate_transition(current_status, new_status):
    allowed_statuses = VALID_TRANSITIONS.get(current_status, set())

    if new_status not in allowed_statuses:
        raise ValidationError({
            "code": "INVALID_STATUS_TRANSITION",
            "detail": (
                f"Cannot change booking status "
                f"from {current_status} to {new_status}."
            ),
            "current_status": current_status,
            "requested_status": new_status,
        })

    return True


@transaction.atomic
def transition_booking(booking_id, new_status):
    booking = (
        Booking.objects
        .select_for_update()
        .get(pk=booking_id)
    )

    validate_transition(
        booking.status,
        new_status
    )

    booking.status = new_status
    booking.save(update_fields=["status", "updated_at"])

    return booking