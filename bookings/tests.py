from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from bookings.models import Booking
from services.models import Service
from rest_framework.test import APITestCase
from django.test import TransactionTestCase
from concurrent.futures import ThreadPoolExecutor
from django.db import close_old_connections, connection
from django.db import IntegrityError
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
                "booking_date": "2026-10-01",
                "booking_time": "10:00:00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "PENDING")
    def test_invalid_completed_to_pending(self):
        booking = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service=self.service,
            booking_date="2026-10-01",
            booking_time="10:00:00",
            amount=500,
            status="COMPLETED",
        )

        response = self.client.patch(
            f"/api/v1/bookings/{booking.id}/status/",
            {"status": "PENDING"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
    def test_booking_uuid_is_unique(self):
        booking1 = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service=self.service,
            booking_date="2026-10-20",
            booking_time="10:00:00",
            amount=500,
            status="PENDING",
        )

        booking2 = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service=self.service,
            booking_date="2026-10-21",
            booking_time="11:00:00",
            amount=500,
            status="PENDING",
        )

        self.assertNotEqual(
            booking1.uuid,
            booking2.uuid
        )

    def test_booking_status_choices_are_valid(self):
        valid_statuses = {
            "PENDING",
            "CONFIRMED",
            "IN_PROGRESS",
            "COMPLETED",
            "CANCELLED",
            "PAYMENT_FAILED",
        }

        model_statuses = {
            value
            for value, label in Booking.STATUS_CHOICES
        }

        self.assertEqual(
            model_statuses,
            valid_statuses
        )

    def test_invalid_cancelled_to_completed(self):
        booking = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service=self.service,
            booking_date="2026-10-02",
            booking_time="10:00:00",
            amount=500,
            status="CANCELLED",
        )

        response = self.client.patch(
            f"/api/v1/bookings/{booking.id}/status/",
            {"status": "COMPLETED"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_invalid_payment_failed_to_started(self):
        booking = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service=self.service,
            booking_date="2026-10-03",
            booking_time="10:00:00",
            amount=500,
            status="PAYMENT_FAILED",
        )

        response = self.client.patch(
            f"/api/v1/bookings/{booking.id}/status/",
            {"status": "IN_PROGRESS"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
class BookingConcurrencyTest(TransactionTestCase):

    reset_sequences = True

    def setUp(self):
        self.customer = User.objects.create_user(
            username="concurrent_customer",
            email="concurrent_customer@test.com",
            password="Test@12345"
        )

        self.provider = User.objects.create_user(
            username="concurrent_provider",
            email="concurrent_provider@test.com",
            password="Test@12345"
        )

        self.service = Service.objects.create(
            provider=self.provider,
            name="Concurrent Service",
            description="Concurrency test service",
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
            booking_date="2026-10-10",
            booking_time="10:00:00",
            amount=500,
            status="PENDING",
        )

    def test_concurrent_booking_status_update(self):
        from .workflow import transition_booking

        def update_status(new_status):
            close_old_connections()

            try:
                transition_booking(
                    self.booking.id,
                    new_status
                )
                return "SUCCESS"

            except Exception:
                return "FAILED"

            finally:
                connection.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(
                    update_status,
                    ["CONFIRMED", "PAYMENT_FAILED"]
                )
            )

        self.assertEqual(
            results.count("SUCCESS"),
            1
        )

        self.assertEqual(
            results.count("FAILED"),
            1
        )

        self.booking.refresh_from_db()

        self.assertIn(
            self.booking.status,
            ["CONFIRMED", "PAYMENT_FAILED"]
        )