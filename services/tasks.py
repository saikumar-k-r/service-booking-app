from celery import shared_task
from django.db import transaction

from .models import Service, SavedService
from notifications.models import Notification


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def notify_saved_service_unavailable(self, service_id):
    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return {
            "status": "service_not_found",
            "service_id": service_id,
        }

    saved_services = SavedService.objects.filter(
        service=service
    ).select_related("customer")

    notifications = []

    for saved_service in saved_services:
        notifications.append(
            Notification(
                user=saved_service.customer,
                title="Saved Service Unavailable",
                message=(
                    f"The service '{service.name}' "
                    "is currently unavailable."
                ),
            )
        )

    if notifications:
        with transaction.atomic():
            Notification.objects.bulk_create(notifications)

    return {
        "status": "notifications_created",
        "service_id": service_id,
        "count": len(notifications),
    }