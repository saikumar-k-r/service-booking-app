from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .external_api_service import (
    ExternalAPIService,
    ExternalIntegrationError,
)


class ExternalServiceCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        service_id = request.data.get("service_id")

        if not service_id:
            return Response(
                {"detail": "service_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = ExternalAPIService().check_service(
                service_id=service_id,
                customer_id=request.user.id,
            )

            return Response(
                result,
                status=status.HTTP_200_OK,
            )

        except ExternalIntegrationError as exc:
            return Response(
                {
                    "success": False,
                    "detail": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )