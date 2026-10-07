import hashlib
import json

from django.db import transaction

from .models import IdempotencyKey


class IdempotencyConflict(Exception):
    pass


def request_hash(data):
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def execute_idempotent_request(user, key, data):
    if not key:
        raise IdempotencyConflict("Idempotency-Key header is required.")

    fingerprint = request_hash(data)

    with transaction.atomic():
        record, created = IdempotencyKey.objects.select_for_update().get_or_create(
            user=user,
            key=key,
            defaults={"request_hash": fingerprint},
        )

        if not created:
            if record.request_hash != fingerprint:
                raise IdempotencyConflict(
                    "Idempotency-Key was already used with a different request."
                )

            if record.completed:
                return (
                    record.response_status,
                    record.response_body,
                    True,
                )

        result = {
            "success": True,
            "message": "Operation processed exactly once.",
            "request": data,
        }

        record.response_status = 200
        record.response_body = result
        record.completed = True
        record.save(
            update_fields=[
                "response_status",
                "response_body",
                "completed",
                "updated_at",
            ]
        )

        return 200, result, False