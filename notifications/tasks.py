from celery import shared_task

from .models import Notification


@shared_task
def create_notification(user_id, title, message):
    notification = Notification.objects.create(
        user_id=user_id,
        title=title,
        message=message,
    )

    return notification.id