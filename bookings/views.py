from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Booking
from .serializers import BookingSerializer
from django.db.models import Q
from .workflow import validate_transition
from rest_framework.exceptions import ValidationError
from .workflow import transition_booking


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Booking.objects
            .select_related("customer", "provider", "service")
            .filter(
                Q(customer=self.request.user) |
                Q(provider=self.request.user)
            )
        )

    def perform_create(self, serializer):
        serializer.save()


class BookingDetailView(generics.RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Booking.objects
            .select_related("customer", "provider", "service")
            .filter(customer=self.request.user)
        )

class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = Booking.objects.get(
                pk=pk,
                customer=request.user
            )
        except Booking.DoesNotExist:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if booking.status == "CANCELLED":
            return Response(
                {"detail": "Booking is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.status == "COMPLETED":
            return Response(
                {"detail": "Completed booking cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = "CANCELLED"
        booking.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "detail": "Booking cancelled successfully.",
                "status": booking.status
            },
            status=status.HTTP_200_OK
        )
class BookingStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get("status")

        # Only customer or provider can update
        if (
            booking.customer_id != request.user.id
            and booking.provider_id != request.user.id
        ):
            return Response(
                {"detail": "You are not allowed to update this booking."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            booking = transition_booking(
                booking.id,
                new_status
            )
        except ValidationError as exc:
            return Response(
                exc.detail,
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "detail": "Booking status updated successfully.",
                "booking_id": booking.id,
                "status": booking.status
            },
            status=status.HTTP_200_OK
        )