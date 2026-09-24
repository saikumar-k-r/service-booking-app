from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ProfileImageUploadView

from .views import (
    RegisterView,
    ProfileView,
    ProviderListView,
)

urlpatterns = [
    # Authentication
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Profile
    path("profile/", ProfileView.as_view(), name="profile"),

    # Service Providers
    path("providers/", ProviderListView.as_view(), name="providers"),
    path(
    "profile/image/",
    ProfileImageUploadView.as_view(),
    name="profile-image"
),
]