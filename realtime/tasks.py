from celery import shared_task

from .publisher import publish_booking_status


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def send_booking_status_event(self, user_id, booking_id, status):
    publish_booking_status(
        user_id=user_id,
        booking_id=booking_id,
        status=status,
    )

    return {
        "success": True,
        "booking_id": booking_id,
        "status": status,
    }