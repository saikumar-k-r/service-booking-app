import logging

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class ExternalIntegrationError(Exception):
    """Raised when the external integration fails."""


class ExternalAPIService:
    def __init__(self):
        self.base_url = settings.EXTERNAL_API_BASE_URL.rstrip("/")
        self.timeout = settings.EXTERNAL_API_TIMEOUT

        retry = Retry(
            total=settings.EXTERNAL_API_RETRIES,
            connect=settings.EXTERNAL_API_RETRIES,
            read=settings.EXTERNAL_API_RETRIES,
            status=settings.EXTERNAL_API_RETRIES,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
        )

        self.session = requests.Session()

        adapter = HTTPAdapter(max_retries=retry)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def check_service(self, service_id, customer_id):
        url = f"{self.base_url}/anything"

        payload = {
            "service_id": service_id,
            "customer_id": customer_id,
            "action": "availability_check",
        }

        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, dict):
                raise ExternalIntegrationError(
                    "Invalid response format from external service."
                )

            return {
                "success": True,
                "provider": "httpbin",
                "data": data,
            }

        except requests.Timeout:
            logger.error(
                "External API timeout while checking service %s",
                service_id,
            )
            raise ExternalIntegrationError(
                "External service timed out."
            )

        except requests.RequestException:
            logger.error(
                "External API request failed while checking service %s",
                service_id,
            )
            raise ExternalIntegrationError(
                "External service request failed."
            )

        except ValueError:
            logger.error(
                "External API returned invalid JSON for service %s",
                service_id,
            )
            raise ExternalIntegrationError(
                "External service returned invalid data."
            )
