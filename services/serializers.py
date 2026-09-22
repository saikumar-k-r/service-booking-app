from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = [
            "id",
            "uuid",
            "provider",
            "name",
            "description",
            "category",
            "price",
            "duration",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "uuid",
            "created_at",
            "updated_at",
        ]