from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import DevicePresence
from .publisher import publish_booking_status


class RealtimeTests(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="realtime_user",
            password="TestPass123!",
        )

    def test_device_presence(self):
        presence = DevicePresence.objects.create(
            user=self.user,
            device_id="android-001",
            is_online=True,
        )

        self.assertTrue(presence.is_online)
        self.assertEqual(presence.device_id, "android-001")

    def test_multiple_devices(self):
        DevicePresence.objects.create(
            user=self.user,
            device_id="android-001",
            is_online=True,
        )

        DevicePresence.objects.create(
            user=self.user,
            device_id="web-001",
            is_online=True,
        )

        self.assertEqual(
            DevicePresence.objects.filter(user=self.user).count(),
            2,
        )

    def test_event_publisher(self):
        # Verifies publisher can be called without raising an exception.
        publish_booking_status(
            self.user.id,
            101,
            "CONFIRMED",
        )