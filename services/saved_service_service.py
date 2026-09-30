from django.db import IntegrityError, transaction

from .models import SavedService, Service


def save_service_for_customer(customer, service_id):
    service = Service.objects.filter(
        pk=service_id,
        status=True,
        is_active=True
    ).first()

    if service is None:
        return None, "SERVICE_NOT_FOUND"

    try:
        with transaction.atomic():
            saved_service = SavedService.objects.create(
                customer=customer,
                service=service
            )
    except IntegrityError:
        return None, "ALREADY_SAVED"

    return saved_service, None


def get_saved_services_for_customer(customer):
    return (
        SavedService.objects
        .filter(customer=customer)
        .select_related("service")
        .order_by("-created_at")
    )


def remove_saved_service(customer, saved_service_id):
    deleted, _ = SavedService.objects.filter(
        pk=saved_service_id,
        customer=customer
    ).delete()

    return deleted > 0
