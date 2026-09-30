from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Service, SavedService
from notifications.models import Notification


class ServiceBasicTest(TestCase):

    def test_service_app(self):
        self.assertTrue(True)
class SavedServiceAPITest(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.customer = User.objects.create_user(
    username="saved_customer",
    email="saved_customer@test.com",
    password="Test@12345"
)

        self.other_customer = User.objects.create_user(
    username="other_customer",
    email="other_customer@test.com",
    password="Test@12345"
)

        self.service = Service.objects.create(
            provider=self.customer,
            name="Test Service",
            description="Test service",
            category="Cleaning",
            price=500,
            duration=60,
            status=True,
            is_active=True,
        )

        self.url = "/api/v1/services/saved-services/"

    def test_save_service(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            self.url,
            {"service": self.service.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            SavedService.objects.filter(
                customer=self.customer,
                service=self.service,
            ).exists()
        )

    def test_duplicate_save(self):
        self.client.force_authenticate(user=self.customer)

        SavedService.objects.create(
            customer=self.customer,
            service=self.service,
        )

        response = self.client.post(
            self.url,
            {"service": self.service.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_list_saved_services(self):
        self.client.force_authenticate(user=self.customer)

        SavedService.objects.create(
            customer=self.customer,
            service=self.service,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

    def test_remove_saved_service(self):
        self.client.force_authenticate(user=self.customer)

        saved = SavedService.objects.create(
            customer=self.customer,
            service=self.service,
        )

        response = self.client.delete(
            f"{self.url}{saved.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            SavedService.objects.filter(
                id=saved.id
            ).exists()
        )

    def test_unauthorized_access(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_service_not_found(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            self.url,
            {"service": 999999},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )