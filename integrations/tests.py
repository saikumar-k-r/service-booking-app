import requests

from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .external_api_service import (
    ExternalAPIService,
    ExternalIntegrationError,
)


class ExternalIntegrationTests(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
    username="integration_test",
    email="integration@test.com",
    password="TestPass123!"
)

        self.client.force_authenticate(user=self.user)

        self.url = "/api/v1/integrations/external/check/"

    @patch("integrations.external_api_service.requests.Session.post")
    def test_successful_external_api(self, mock_post):

        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "json": {
                "service_id": 101,
                "customer_id": self.user.id,
            }
        }

        mock_post.return_value = response

        api_response = self.client.post(
            self.url,
            {"service_id": 101},
            format="json",
        )

        self.assertEqual(
            api_response.status_code,
            status.HTTP_200_OK,
        )

    def test_missing_service_id(self):

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    @patch("integrations.external_api_service.requests.Session.post")
    def test_external_request_failure(self, mock_post):

        mock_post.side_effect = requests.RequestException(
            "connection failed"
        )

        response = self.client.post(
            self.url,
            {"service_id": 101},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_502_BAD_GATEWAY,
        )

    @patch("integrations.external_api_service.requests.Session.post")
    def test_timeout_handling(self, mock_post):

        mock_post.side_effect = requests.Timeout()

        with self.assertRaises(ExternalIntegrationError):

            ExternalAPIService().check_service(
                service_id=101,
                customer_id=self.user.id,
            )

    @patch("integrations.external_api_service.requests.Session.post")
    def test_invalid_response(self, mock_post):

        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = []

        mock_post.return_value = response

        with self.assertRaises(ExternalIntegrationError):

            ExternalAPIService().check_service(
                service_id=101,
                customer_id=self.user.id,
            )