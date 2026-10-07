from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import CursorPagination

from .models import SyncItem
from .services import execute_idempotent_request, IdempotencyConflict


class ReliableOperationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        key = request.headers.get("Idempotency-Key")

        try:
            response_status, data, replay = execute_idempotent_request(
                request.user,
                key,
                request.data,
            )
        except IdempotencyConflict as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_409_CONFLICT,
            )

        response = Response(data, status=response_status)

        if replay:
            response["Idempotent-Replay"] = "true"
        else:
            response["Idempotent-Replay"] = "false"

        return response


class SyncCursorPagination(CursorPagination):
    page_size = 20
    page_size_query_param = "limit"
    max_page_size = 50
    ordering = "updated_at"


class IncrementalSyncView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = SyncItem.objects.all()

        since = request.query_params.get("since")

        if since:
            queryset = queryset.filter(updated_at__gt=since)

        paginator = SyncCursorPagination()
        page = paginator.paginate_queryset(queryset, request)

        results = [
            {
                "id": item.resource_id,
                "type": item.resource_type,
                "version": item.version,
                "updated_at": item.updated_at,
                "deleted": item.is_deleted,
                "data": item.payload,
            }
            for item in page
        ]

        return paginator.get_paginated_response({
            "sync": True,
            "items": results,
        })