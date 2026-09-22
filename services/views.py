from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Service
from .serializers import ServiceSerializer
from .pagination import ServicePagination


class ServiceListCreateView(generics.ListCreateAPIView):

    serializer_class = ServiceSerializer
    pagination_class = ServicePagination

    # SearchFilter
    filter_backends = [SearchFilter]

    search_fields = [
        "name",
        "description",
        "category",
    ]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated()]

    def get_queryset(self):

        queryset = Service.objects.filter(
            status=True,
            is_active=True
        )

        # Category filter
        category = self.request.query_params.get("category")

        if category:
            queryset = queryset.filter(
                category__iexact=category
            )

        # Provider filter
        provider = self.request.query_params.get("provider")

        if provider:
            queryset = queryset.filter(
                provider_id=provider
            )

        # Minimum price
        min_price = self.request.query_params.get("min_price")

        if min_price:
            queryset = queryset.filter(
                price__gte=min_price
            )

        # Maximum price
        max_price = self.request.query_params.get("max_price")

        if max_price:
            queryset = queryset.filter(
                price__lte=max_price
            )

        # Sorting
        ordering = self.request.query_params.get(
            "ordering",
            "-created_at"
        )

        allowed_ordering = [
            "price",
            "-price",
            "created_at",
            "-created_at",
            "name",
            "-name",
        ]

        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)

        return queryset


class ServiceDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    queryset = Service.objects.all()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):

        # Soft delete
        instance.is_active = False
        instance.status = False
        instance.save()