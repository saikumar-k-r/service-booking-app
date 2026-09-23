from rest_framework import serializers
from .models import Payment
from bookings.models import Booking


class PaymentInitiateSerializer(serializers.Serializer):

    booking = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all()
    )

    payment_method = serializers.ChoiceField(
        choices=Payment.PaymentMethod.choices,
        default=Payment.PaymentMethod.MOCK
    )

    def validate(self, attrs):

        request = self.context["request"]
        booking = attrs["booking"]

        # Booking must belong to logged-in user
        if booking.customer_id != request.user.id:
            raise serializers.ValidationError(
                "You can only pay for your own booking."
            )

        # Booking must be payable
        if booking.status not in ["PENDING"]:
            raise serializers.ValidationError(
                "Booking is not payable."
            )

        # Existing successful payment check
        if Payment.objects.filter(
            booking=booking,
            payment_status=Payment.PaymentStatus.SUCCESS
        ).exists():
            raise serializers.ValidationError(
                "Booking has already been paid."
            )

        return attrs