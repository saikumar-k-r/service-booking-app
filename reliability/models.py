from django.conf import settings
from django.db import models


class IdempotencyKey(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="idempotency_keys",
    )
    key = models.CharField(max_length=255)
    request_hash = models.CharField(max_length=64)
    response_status = models.PositiveSmallIntegerField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "key"],
                name="unique_user_idempotency_key",
            )
        ]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]


class SyncItem(models.Model):
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    version = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["resource_type", "resource_id"],
                name="unique_sync_resource",
            )
        ]
        ordering = ["updated_at", "id"]