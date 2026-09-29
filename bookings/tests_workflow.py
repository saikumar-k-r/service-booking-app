import threading

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TransactionTestCase

from bookings.models import Booking
from bookings.workflow import transition_booking
from services.models import Service


User = get_user_model()


class BookingWorkflowTests(TransactionTestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
            username="workflow_customer",
            email="workflow_customer@example.com",
            password="Test@12345",
            role="CUSTOMER",
        )

        self.provider = User.objects.create_user(
            username="workflow_provider",
            email="workflow_provider@example.com",
            password="Test@12345",
            role="PROVIDER",
        )

        self.service = Service.objects.create(
            provider=self.provider,
            category="Cleaning",
            name="Workflow Test Service",
            description="Service used for workflow testing",
            price="100.00",
            duration=60,
            status=True,
            is_active=True,
        )

        self.booking = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service=self.service,
            booking_date="2026-10-01",
            booking_time="10:00:00",
            amount="100.00",
            status="PENDING",
        )

    def test_pending_to_confirmed_allowed(self):
        booking = transition_booking(
            self.booking.id,
            "CONFIRMED",
        )

        self.assertEqual(
            booking.status,
            "CONFIRMED",
        )

    def test_confirmed_to_in_progress_allowed(self):
        self.booking.status = "CONFIRMED"
        self.booking.save(update_fields=["status"])

        booking = transition_booking(
            self.booking.id,
            "IN_PROGRESS",
        )

        self.assertEqual(
            booking.status,
            "IN_PROGRESS",
        )

    def test_in_progress_to_completed_allowed(self):
        self.booking.status = "IN_PROGRESS"
        self.booking.save(update_fields=["status"])

        booking = transition_booking(
            self.booking.id,
            "COMPLETED",
        )

        self.assertEqual(
            booking.status,
            "COMPLETED",
        )

    def test_completed_to_pending_rejected(self):
        self.booking.status = "COMPLETED"
        self.booking.save(update_fields=["status"])

        with self.assertRaises(Exception):
            transition_booking(
                self.booking.id,
                "PENDING",
            )

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            "COMPLETED",
        )

    def test_cancelled_to_completed_rejected(self):
        self.booking.status = "CANCELLED"
        self.booking.save(update_fields=["status"])

        with self.assertRaises(Exception):
            transition_booking(
                self.booking.id,
                "COMPLETED",
            )

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            "CANCELLED",
        )

    def test_payment_failed_to_in_progress_rejected(self):
        self.booking.status = "PAYMENT_FAILED"
        self.booking.save(update_fields=["status"])

        with self.assertRaises(Exception):
            transition_booking(
                self.booking.id,
                "IN_PROGRESS",
            )

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            "PAYMENT_FAILED",
        )

    def test_invalid_transition_rolls_back(self):
        self.assertEqual(
            self.booking.status,
            "PENDING",
        )

        with self.assertRaises(Exception):
            transition_booking(
                self.booking.id,
                "IN_PROGRESS",
            )

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            "PENDING",
        )


class BookingConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.customer = User.objects.create_user(
            username="concurrency_customer",
            email="concurrency_customer@example.com",
            password="Test@12345",
            role="CUSTOMER",
        )

        self.provider = User.objects.create_user(
            username="concurrency_provider",
            email="concurrency_provider@example.com",
            password="Test@12345",
            role="PROVIDER",
        )

        self.service = Service.objects.create(
            provider=self.provider,
            category="Cleaning",
            name="Concurrency Test Service",
            description="Service used for concurrency testing",
            price="100.00",
            duration=60,
            status=True,
            is_active=True,
        )

        self.booking = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service=self.service,
            booking_date="2026-10-01",
            booking_time="10:00:00",
            amount="100.00",
            status="PENDING",
        )

    def test_concurrent_booking_confirmation_only_one_valid_transition(
        self
    ):
        results = []
        errors = []

        def confirm_booking():
            try:
                booking = transition_booking(
                    self.booking.id,
                    "CONFIRMED",
                )

                results.append(
                    booking.status
                )

            except Exception as exc:
                errors.append(
                    str(exc)
                )

            finally:
                connection.close()

        thread_1 = threading.Thread(
            target=confirm_booking
        )

        thread_2 = threading.Thread(
            target=confirm_booking
        )

        thread_1.start()
        thread_2.start()

        thread_1.join()
        thread_2.join()

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            "CONFIRMED",
        )

        self.assertEqual(
            len(results),
            1,
            "Only one concurrent request should successfully confirm the booking.",
        )

        self.assertEqual(
            len(errors),
            1,
            "The second concurrent request must be rejected.",
        )