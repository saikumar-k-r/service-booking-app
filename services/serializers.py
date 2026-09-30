from rest_framework import serializers
from .models import Service, ServiceImage, SavedService


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
        ]

        read_only_fields = [
            "id",
            "uuid",
            "provider",
        ]


class ServiceImageSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceImage
        fields = [
            "id",
            "image_url",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "image_url",
            "created_at",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")

        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)

        return None
class SavedServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = SavedService
        fields = [
            "id",
            "customer",
            "service",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "customer",
            "created_at",
        ]