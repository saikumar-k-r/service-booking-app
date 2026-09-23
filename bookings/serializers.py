from rest_framework import serializers
from django.utils import timezone

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):

    customer = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    provider = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Booking

        fields = [
            "uuid",
            "customer",
            "provider",
            "service",
            "booking_date",
            "booking_time",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "uuid",
            "customer",
            "provider",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        service = attrs.get("service")
        booking_date = attrs.get("booking_date")
        booking_time = attrs.get("booking_time")

        # Service validation
        if not service.is_active:
            raise serializers.ValidationError(
                "Selected service is not active."
            )

        # Provider validation
        if not service.provider.is_active:
            raise serializers.ValidationError(
                "Service provider is not active."
            )

        # Past date validation
        today = timezone.localdate()

        if booking_date < today:
            raise serializers.ValidationError(
                "Booking date cannot be in the past."
            )

        # Same-day time validation
        if booking_date == today:

            current_time = timezone.localtime().time()

            if booking_time <= current_time:
                raise serializers.ValidationError(
                    "Booking time must be in the future."
                )

        # Provider booking conflict
        conflict = Booking.objects.filter(
            provider=service.provider,
            booking_date=booking_date,
            booking_time=booking_time,
            status__in=[
                "PENDING",
                "CONFIRMED"
            ]
        ).exists()

        if conflict:
            raise serializers.ValidationError(
                "Provider is already booked for this time."
            )

        return attrs

    def create(self, validated_data):

        request = self.context["request"]

        service = validated_data["service"]

        return Booking.objects.create(
            customer=request.user,
            provider=service.provider,
            service=service,
            amount=service.price,
            **{
                key: value
                for key, value in validated_data.items()
                if key != "service"
            }
        )
    def validate_status(self, value):
      current_status = self.instance.status if self.instance else None

      allowed_transitions = {
        "PENDING": ["CONFIRMED", "CANCELLED", "PAYMENT_FAILED"],
        "CONFIRMED": ["IN_PROGRESS", "CANCELLED"],
        "IN_PROGRESS": ["COMPLETED"],
        "COMPLETED": [],
        "CANCELLED": [],
        "PAYMENT_FAILED": [],
    }

      if current_status and value not in allowed_transitions[current_status]:
        raise serializers.ValidationError(
            f"Invalid status transition: {current_status} -> {value}"
        )

      return value