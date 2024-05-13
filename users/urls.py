from django.urls import path

from .views import (
    SignInAPIView,
    SignOutAPIView,
    SignUpAPIView,
    TokenRefreshView,
    UserDetailView,
    UserProfileImageView,
)

urlpatterns = [
    path("sign-up/", SignUpAPIView.as_view(), name="sign-up"),
    path("sign-in/", SignInAPIView.as_view(), name="sign-in"),
    path("sign-out/", SignOutAPIView.as_view(), name="sign-out"),
    path("detail/", UserDetailView.as_view(), name="user_detail"),
    path("token-refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile-image", UserProfileImageView.as_view(), name="profile-image"),

]
