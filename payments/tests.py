from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from bookings.models import Booking
from services.models import Service
from .models import Payment


User = get_user_model()


class PaymentIdempotencyTest(APITestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
            username="payment_customer",
            email="payment_customer@test.com",
            password="Test@12345"
        )

        self.provider = User.objects.create_user(
            username="payment_provider",
            email="payment_provider@test.com",
            password="Test@12345"
        )

        self.service = Service.objects.create(
            provider=self.provider,
            name="Payment Test Service",
            description="Payment idempotency test",
            category="Cleaning",
            price=500,
            duration=60,
            status=True,
            is_active=True,
        )

        self.booking = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service=self.service,
            booking_date="2026-10-15",
            booking_time="10:00:00",
            amount=500,
            status="PENDING",
        )

        self.client.force_authenticate(
            user=self.customer
        )

    def test_payment_initiation_is_idempotent(self):

        data = {
            "booking": self.booking.id,
            "payment_method": "MOCK"
        }

        first_response = self.client.post(
            "/api/v1/payments/initiate/",
            data,
            format="json"
        )

        second_response = self.client.post(
            "/api/v1/payments/initiate/",
            data,
            format="json"
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK
        )

        # Only one payment must exist.
        self.assertEqual(
            Payment.objects.filter(
                booking=self.booking
            ).count(),
            1
        )

        # Retry must return the same payment.
        self.assertEqual(
            first_response.data["payment_id"],
            second_response.data["payment_id"]
        )

        self.assertEqual(
            first_response.data["transaction_id"],
            second_response.data["transaction_id"]
        )