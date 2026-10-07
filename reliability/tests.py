from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import IdempotencyKey, SyncItem


class ReliabilityTests(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
    username="reliabilitytest",
    email="reliability@test.com",
    password="TestPass123!",
)

        self.client.force_authenticate(user=self.user)

        self.operation_url = "/api/v1/reliability/reliable-operation/"
        self.sync_url = "/api/v1/reliability/sync/"

    def test_missing_idempotency_key(self):
        response = self.client.post(
            self.operation_url,
            {"booking_id": 101},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

    def test_duplicate_request_returns_same_response(self):
        headers = {"HTTP_IDEMPOTENCY_KEY": "mobile-request-001"}

        first = self.client.post(
            self.operation_url,
            {"booking_id": 101},
            format="json",
            **headers,
        )

        second = self.client.post(
            self.operation_url,
            {"booking_id": 101},
            format="json",
            **headers,
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data, second.data)
        self.assertEqual(
            second["Idempotent-Replay"],
            "true",
        )

        self.assertEqual(
            IdempotencyKey.objects.filter(
                user=self.user,
                key="mobile-request-001",
            ).count(),
            1,
        )

    def test_same_key_different_payload_rejected(self):
        headers = {"HTTP_IDEMPOTENCY_KEY": "mobile-request-002"}

        self.client.post(
            self.operation_url,
            {"booking_id": 101},
            format="json",
            **headers,
        )

        response = self.client.post(
            self.operation_url,
            {"booking_id": 999},
            format="json",
            **headers,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

    def test_sync_endpoint(self):
        SyncItem.objects.create(
            resource_type="booking",
            resource_id="101",
            payload={"status": "confirmed"},
        )

        response = self.client.get(self.sync_url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["results"]["sync"])

    def test_sync_deleted_item(self):
        SyncItem.objects.create(
            resource_type="booking",
            resource_id="102",
            payload={},
            is_deleted=True,
            version=2,
        )

        response = self.client.get(self.sync_url)

        self.assertEqual(response.status_code, 200)