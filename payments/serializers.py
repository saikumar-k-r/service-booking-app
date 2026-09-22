from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "booking",
            "amount",
            "transaction_reference",
            "status",
            "paid_at",
            "created_at",
        ]
        read_only_fields = ["status", "paid_at", "created_at"]

    def validate_booking(self, booking):
        if booking.customer != self.context["request"].user:
            raise serializers.ValidationError(
                "You can only pay for your own booking."
            )
        return booking