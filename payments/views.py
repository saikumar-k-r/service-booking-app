from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Payment
from .serializers import PaymentSerializer


class PaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            booking__customer=self.request.user
        )

    def perform_create(self, serializer):
        booking = serializer.validated_data["booking"]
        serializer.save(
            amount=booking.total_amount,
            transaction_reference=f"TXN-{booking.id}-{self.request.user.id}",
        )


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            booking__customer=self.request.user
        )