from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Service
from .tasks import notify_saved_service_unavailable


@receiver(pre_save, sender=Service)
def service_before_save(sender, instance, **kwargs):
    if not instance.pk:
        instance._became_unavailable = False
        return

    try:
        previous = sender.objects.get(pk=instance.pk)

        previous_available = (
            previous.status and previous.is_active
        )

        current_available = (
            instance.status and instance.is_active
        )

        instance._became_unavailable = (
            previous_available and not current_available
        )

    except sender.DoesNotExist:
        instance._became_unavailable = False


@receiver(post_save, sender=Service)
def service_after_save(sender, instance, **kwargs):
    if getattr(instance, "_became_unavailable", False):
        notify_saved_service_unavailable.delay(instance.id)