from django.urls import path

from .views import (
    SignInAPIView,
    KakaoSignInView,
    SignOutAPIView,
    SignUpAPIView,
    EmailCheckAPIView,
    TokenRefreshView,
    UserDetailView,
    UserProfileImageView,
)

urlpatterns = [
    path("sign-up/", SignUpAPIView.as_view(), name="sign-up"),
    path("email-check/", EmailCheckAPIView.as_view(), name="email-check"),
    path("sign-in/", SignInAPIView.as_view(), name="sign-in"),
    path("kakao/sign-in/", KakaoSignInView.as_view(), name="kakao-sign-in"),
    path("sign-out/", SignOutAPIView.as_view(), name="sign-out"),
    path("detail/", UserDetailView.as_view(), name="user-detail"),
    path("token-refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("profile-image/", UserProfileImageView.as_view(), name="profile-image"),
]
