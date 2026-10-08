from django.conf import settings
from django.db import models


class DevicePresence(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="device_presences",
    )
    device_id = models.CharField(max_length=255)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    connected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "device_id"],
                name="unique_user_device_presence",
            )
        ]