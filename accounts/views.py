from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import User, Profile
from .serializers import RegisterSerializer, ProfileSerializer


class RegisterView(generics.CreateAPIView):
    """
    Register a new user.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the logged-in user's profile.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = Profile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class ProviderListView(generics.ListAPIView):
    """
    List service providers.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(
            user__role="PROVIDER"
        )
class ProfileImageUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        image_url = request.data.get("profile_image_url")

        if image_url:
            profile = request.user.profile
            profile.profile_image_url = image_url
            profile.save(update_fields=["profile_image_url"])

            return Response({
                "success": True,
                "message": "Profile image URL saved successfully",
                "error_code": None,
                "data": {
                    "profile_image_url": profile.profile_image_url
                }
            }, status=200)

        image = request.FILES.get("profile_image")

        if not image:
            return Response({
                "success": False,
                "message": "Image is required",
                "error_code": "IMAGE_REQUIRED",
                "data": None
            }, status=400)

        profile = request.user.profile
        profile.profile_image = image
        profile.save()

        return Response({
            "success": True,
            "message": "Profile image uploaded successfully",
            "error_code": None,
            "data": {
                "profile_image": profile.profile_image.url
            }
        }, status=200)