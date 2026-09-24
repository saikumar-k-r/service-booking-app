from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from .models import Service, ServiceImage
from .serializers import ServiceSerializer, ServiceImageSerializer
from .pagination import ServicePagination
from .utils.responses import success_response, error_response


class StandardResponseMixin:

    def handle_exception(self, exc):
        response = super().handle_exception(exc)

        if response is None:
            return response

        detail = response.data.get(
            "detail",
            "Something went wrong"
        )

        if isinstance(detail, list):
            message = " ".join(str(x) for x in detail)
        elif isinstance(detail, dict):
            message = str(detail)
        else:
            message = str(detail)

        error_code = "API_ERROR"

        if response.status_code == 400:
            error_code = "VALIDATION_ERROR"
        elif response.status_code == 401:
            error_code = "AUTHENTICATION_REQUIRED"
        elif response.status_code == 403:
            error_code = "PERMISSION_DENIED"
        elif response.status_code == 404:
            error_code = "NOT_FOUND"
        elif response.status_code == 405:
            error_code = "METHOD_NOT_ALLOWED"

        return error_response(
            message=message,
            error_code=error_code,
            status=response.status_code
        )


class ServiceListCreateView(
    StandardResponseMixin,
    generics.ListCreateAPIView
):

    serializer_class = ServiceSerializer
    pagination_class = ServicePagination
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

        category = self.request.query_params.get("category")

        if category:
            queryset = queryset.filter(
                category__iexact=category
            )

        provider = self.request.query_params.get("provider")

        if provider:
            queryset = queryset.filter(
                provider_id=provider
            )

        min_price = self.request.query_params.get("min_price")

        if min_price:
            queryset = queryset.filter(
                price__gte=min_price
            )

        max_price = self.request.query_params.get("max_price")

        if max_price:
            queryset = queryset.filter(
                price__lte=max_price
            )

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

    def list(self, request, *args, **kwargs):

        response = super().list(
            request,
            *args,
            **kwargs
        )

        return success_response(
            data=response.data,
            message="Services retrieved successfully"
        )

    def create(self, request, *args, **kwargs):

        response = super().create(
            request,
            *args,
            **kwargs
        )

        return success_response(
            data=response.data,
            message="Service created successfully",
            status=status.HTTP_201_CREATED
        )


class ServiceDetailView(
    StandardResponseMixin,
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    queryset = Service.objects.all()

    def retrieve(self, request, *args, **kwargs):

        response = super().retrieve(
            request,
            *args,
            **kwargs
        )

        return success_response(
            data=response.data,
            message="Service retrieved successfully"
        )

    def update(self, request, *args, **kwargs):

        response = super().update(
            request,
            *args,
            **kwargs
        )

        return success_response(
            data=response.data,
            message="Service updated successfully"
        )

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        instance.is_active = False
        instance.status = False
        instance.save()

        return success_response(
            data=None,
            message="Service deleted successfully"
        )


class ServiceImageListCreateView(
    StandardResponseMixin,
    generics.ListCreateAPIView
):

    serializer_class = ServiceImageSerializer
    permission_classes = [IsAuthenticated]

    parser_classes = [
        MultiPartParser,
        FormParser
    ]

    def get_queryset(self):

        return ServiceImage.objects.filter(
            service_id=self.kwargs["service_id"]
        )

    def list(self, request, *args, **kwargs):

        response = super().list(
            request,
            *args,
            **kwargs
        )

        return success_response(
            data=response.data,
            message="Service images retrieved successfully"
        )

    def perform_create(self, serializer):

        service = get_object_or_404(
            Service,
            pk=self.kwargs["service_id"]
        )

        if service.provider != self.request.user:

            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Only the service provider can upload images."
            )

        serializer.save(service=service)

    def create(self, request, *args, **kwargs):

        response = super().create(
            request,
            *args,
            **kwargs
        )

        return success_response(
            data=response.data,
            message="Service image uploaded successfully",
            status=status.HTTP_201_CREATED
        )


class ServiceImageDeleteView(
    StandardResponseMixin,
    generics.DestroyAPIView
):

    serializer_class = ServiceImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return ServiceImage.objects.filter(
            service_id=self.kwargs["service_id"],
            service__provider=self.request.user
        )

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        instance.delete()

        return success_response(
            data=None,
            message="Service image deleted successfully"
        )