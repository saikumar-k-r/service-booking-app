from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from services.models import Service

User = get_user_model()


class BookingAPITest(APITestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
           username="testcustomer",
           email="testcustomer_booking@test.com",
           password="Test@12345"
  )

        self.provider = User.objects.create_user(
           username="testprovider",
           email="testprovider_booking@test.com",
           password="Test@12345"
     )

        self.service = Service.objects.create(
            provider=self.provider,
            name="Test Service",
            description="Test service",
            category="Cleaning",
            price=500,
            duration=60,
            status=True,
            is_active=True,
        )

        self.client.force_authenticate(user=self.customer)

    def test_booking_create(self):
        response = self.client.post(
            "/api/v1/bookings/",
            {
                "service": self.service.id,
                "booking_date": "2026-09-25",
                "booking_time": "10:00:00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "PENDING")