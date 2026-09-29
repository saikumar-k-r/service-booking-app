from datetime import timedelta
from datetime import time
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase
from bookings.models import Booking
from services.models import Service
from accounts.models import Profile

from rest_framework_simplejwt.tokens import AccessToken


User = get_user_model()


class AuthenticationAuditTests(APITestCase):

    def setUp(self):
        self.password = "Test@12345"
        self.new_password = "NewTest@12345"

        self.user = User.objects.create_user(
            username="securitytest",
            email="securitytest@example.com",
            password=self.password,
        )

        self.login_url = "/api/v1/auth/login/"
        self.refresh_url = "/api/v1/auth/token/refresh/"
        self.logout_url = "/api/v1/auth/logout/"
        self.password_url = "/api/v1/auth/password/change/"
        self.profile_url = "/api/v1/auth/profile/"

    def login(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "securitytest",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"Login failed: {response.data}",
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        return response.data

    # =========================================================
    # 1. MISSING TOKEN
    # =========================================================

    def test_missing_token_rejected(self):
        response = self.client.get(self.profile_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # =========================================================
    # 2. INVALID TOKEN
    # =========================================================

    def test_invalid_token_rejected(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer invalid-token"
        )

        response = self.client.get(self.profile_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # =========================================================
    # 3. EXPIRED TOKEN
    # =========================================================

    def test_expired_token_rejected(self):
        token = AccessToken.for_user(self.user)

        token.set_exp(
            from_time=timezone.now() - timedelta(minutes=5)
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(token)}"
        )

        response = self.client.get(self.profile_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # =========================================================
    # 4. REFRESH TOKEN
    # =========================================================

    def test_refresh_token(self):
        tokens = self.login()

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"Refresh failed: {response.data}",
        )

        self.assertIn(
            "access",
            response.data,
        )

    # =========================================================
    # 5. LOGOUT + TOKEN BLACKLIST
    # =========================================================

    def test_logout_blacklists_refresh_token(self):
        tokens = self.login()

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}"
        )

        response = self.client.post(
            self.logout_url,
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        # Logout implementations commonly return either
        # 200 OK or 205 RESET CONTENT.
        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_205_RESET_CONTENT,
            ],
            msg=f"Logout failed: {response.data}",
        )

        # The same refresh token MUST NOT work after logout.
        response = self.client.post(
            self.refresh_url,
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            msg=f"Refresh token was not blacklisted: {response.data}",
        )

    # =========================================================
    # 6. PASSWORD CHANGE
    # =========================================================

    def test_password_change(self):
        tokens = self.login()

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}"
        )

        response = self.client.post(
            self.password_url,
            {
                "old_password": self.password,
                "new_password": self.new_password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=(
                f"Password change failed. "
                f"Status={response.status_code}, "
                f"Response={response.data}"
            ),
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(self.new_password)
        )

    # =========================================================
    # 7. WRONG OLD PASSWORD
    # =========================================================

    def test_wrong_old_password_rejected(self):
        tokens = self.login()

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}"
        )

        response = self.client.post(
            self.password_url,
            {
                "old_password": "WrongPassword@123",
                "new_password": self.new_password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=f"Invalid old password was accepted: {response.data}",
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(self.password)
        )

        self.assertFalse(
            self.user.check_password(self.new_password)
        )

class IDORSecurityTests(APITestCase):

    def setUp(self):
        self.password = "Test@12345"

        # Customer A
        self.customer_a = User.objects.create_user(
            username="customer_a",
            email="customer_a@example.com",
            password=self.password,
            role="CUSTOMER",
        )

        # Customer B
        self.customer_b = User.objects.create_user(
            username="customer_b",
            email="customer_b@example.com",
            password=self.password,
            role="CUSTOMER",
        )

        # Provider A
        self.provider_a = User.objects.create_user(
            username="provider_a",
            email="provider_a@example.com",
            password=self.password,
            role="PROVIDER",
        )

        # Provider B
        self.provider_b = User.objects.create_user(
            username="provider_b",
            email="provider_b@example.com",
            password=self.password,
            role="PROVIDER",
        )

        # Profiles
        self.profile_a = Profile.objects.create(
            user=self.customer_a,
            full_name="Customer A",
        )

        self.profile_b = Profile.objects.create(
            user=self.customer_b,
            full_name="Customer B",
        )

        # Provider B service
        self.service_b = Service.objects.create(
            provider=self.provider_b,
            category="Cleaning",
            name="Provider B Service",
            description="Provider B private service",
            price=500,
            duration=60,
            status=True,
            is_active=True,
        )

        # Customer B booking
        self.booking_b = Booking.objects.create(
            customer=self.customer_b,
            provider=self.provider_b,
            service=self.service_b,
            booking_date=timezone.localdate(),
            booking_time=time(10, 0),
            amount=500,
            status="PENDING",
        )

    # ---------------------------------------------------------
    # IDOR 1: Customer A -> Customer B Profile
    # ---------------------------------------------------------
    def test_customer_cannot_access_another_customer_profile(self):

        self.client.force_authenticate(
            user=self.customer_a
        )

        response = self.client.get(
            "/api/v1/auth/profile/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        # The returned profile must belong to Customer A.
        self.assertEqual(
            response.data["user"],
            self.customer_a.id,
        )

        # Customer B's profile must remain untouched.
        self.profile_b.refresh_from_db()

        self.assertEqual(
            self.profile_b.user_id,
            self.customer_b.id,
        )

    # ---------------------------------------------------------
    # IDOR 2: Customer A -> Customer B Booking
    # ---------------------------------------------------------
    def test_customer_cannot_access_another_customer_booking(self):

        self.client.force_authenticate(
            user=self.customer_a
        )

        response = self.client.get(
            f"/api/v1/bookings/{self.booking_b.id}/"
        )

        # BookingDetailView only exposes the logged-in
        # customer's bookings.
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ---------------------------------------------------------
    # IDOR 3: Provider A -> Provider B Service
    # ---------------------------------------------------------
    def test_provider_cannot_modify_another_provider_service(self):

        self.client.force_authenticate(
            user=self.provider_a
        )

        response = self.client.patch(
            f"/api/v1/services/{self.service_b.id}/",
            {
                "name": "Hacked Service"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        # Verify Provider B's service was not changed.
        self.service_b.refresh_from_db()

        self.assertEqual(
            self.service_b.name,
            "Provider B Service",
        )