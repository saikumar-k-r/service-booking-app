from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

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

            return Response(
                {
                    "success": True,
                    "message": "Profile image URL saved successfully",
                    "error_code": None,
                    "data": {
                        "profile_image_url": profile.profile_image_url
                    }
                },
                status=status.HTTP_200_OK
            )

        image = request.FILES.get("profile_image")

        if not image:
            return Response(
                {
                    "success": False,
                    "message": "Image is required",
                    "error_code": "IMAGE_REQUIRED",
                    "data": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = request.user.profile
        profile.profile_image = image
        profile.save()

        return Response(
            {
                "success": True,
                "message": "Profile image uploaded successfully",
                "error_code": None,
                "data": {
                    "profile_image": profile.profile_image.url
                }
            },
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    """
    Logout the authenticated user and blacklist the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                    "detail": "Refresh token is required.",
                    "error_code": "REFRESH_TOKEN_REQUIRED"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)

            token.blacklist()

            return Response(
                {
                    "detail": "Logout successful."
                },
                status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {
                    "detail": "Invalid or expired refresh token.",
                    "error_code": "INVALID_REFRESH_TOKEN"
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordChangeView(APIView):
    """
    Change the authenticated user's password.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        # Support both names:
        # old_password -> security audit / standard API request
        # current_password -> existing API compatibility
        current_password = (
            request.data.get("old_password")
            or request.data.get("current_password")
        )

        new_password = request.data.get("new_password")

        # Required field validation
        if not current_password or not new_password:
            return Response(
                {
                    "detail": (
                        "Current password and new password are required."
                    ),
                    "error_code": "PASSWORD_FIELDS_REQUIRED"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify current password
        if not request.user.check_password(current_password):
            return Response(
                {
                    "detail": "Current password is incorrect.",
                    "error_code": "INVALID_CURRENT_PASSWORD"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent using the same password
        if request.user.check_password(new_password):
            return Response(
                {
                    "detail": "New password must be different from the current password.",
                    "error_code": "PASSWORD_UNCHANGED"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Minimum password length
        if len(new_password) < 8:
            return Response(
                {
                    "detail": "New password must contain at least 8 characters.",
                    "error_code": "PASSWORD_TOO_SHORT"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set and save new password securely
        request.user.set_password(new_password)
        request.user.save(update_fields=["password"])

        return Response(
            {
                "detail": "Password changed successfully.",
                "error_code": None
            },
            status=status.HTTP_200_OK
        )