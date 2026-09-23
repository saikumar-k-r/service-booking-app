import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .serializers import PaymentInitiateSerializer


class PaymentInitiateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = PaymentInitiateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        booking = serializer.validated_data["booking"]
        payment_method = serializer.validated_data["payment_method"]

        payment = Payment.objects.create(
            booking=booking,
            amount=booking.amount,
            transaction_id=uuid.uuid4(),
            payment_status=Payment.PaymentStatus.PENDING,
            payment_method=payment_method
        )

        return Response(
            {
                "message": "Payment initiated successfully.",
                "payment_id": payment.id,
                "transaction_id": str(payment.transaction_id),
                "booking": str(booking.uuid),
                "amount": str(payment.amount),
                "payment_status": payment.payment_status,
                "payment_method": payment.payment_method
            },
            status=status.HTTP_201_CREATED
        )


class MockPaymentProcessView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:
            payment = Payment.objects.get(
                pk=pk,
                booking__customer=request.user
            )
        except Payment.DoesNotExist:
            return Response(
                {"detail": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if payment.payment_status != Payment.PaymentStatus.PENDING:
            return Response(
                {
                    "detail": "Payment is already processed.",
                    "payment_status": payment.payment_status
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mock processing
        outcome = request.data.get("outcome", "SUCCESS").upper()

        if outcome == "FAILED":
            payment.payment_status = Payment.PaymentStatus.FAILED
        else:
            payment.payment_status = Payment.PaymentStatus.SUCCESS

        payment.save(update_fields=["payment_status"])

        return Response(
            {
                "message": "Mock payment processed successfully.",
                "payment_id": payment.id,
                "transaction_id": str(payment.transaction_id),
                "payment_status": payment.payment_status
            },
            status=status.HTTP_200_OK
        )
class PaymentWebhookView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        transaction_id = request.data.get("transaction_id")
        event_status = request.data.get("status")

        if not transaction_id or not event_status:
            return Response(
                {"detail": "transaction_id and status are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.select_related(
                "booking"
            ).get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response(
                {"detail": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if payment.booking.customer != request.user:
            return Response(
                {"detail": "You are not allowed to update this payment."},
                status=status.HTTP_403_FORBIDDEN
            )

        event_status = event_status.upper()

        if event_status not in [
            Payment.PaymentStatus.SUCCESS,
            Payment.PaymentStatus.FAILED,
        ]:
            return Response(
                {"detail": "Invalid payment event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if payment.payment_status != Payment.PaymentStatus.PENDING:
            return Response(
                {
                    "detail": "Payment has already been processed.",
                    "payment_status": payment.payment_status
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment.payment_status = event_status
        payment.save(update_fields=["payment_status"])

        if event_status == Payment.PaymentStatus.SUCCESS:
            payment.booking.status = "CONFIRMED"
            payment.booking.save(update_fields=["status", "updated_at"])

        elif event_status == Payment.PaymentStatus.FAILED:
            payment.booking.status = "PENDING"
            payment.booking.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "message": "Payment webhook processed successfully.",
                "payment_status": payment.payment_status,
                "booking_status": payment.booking.status
            },
            status=status.HTTP_200_OK
        )