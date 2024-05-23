import requests
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from config.settings import env

from .models import CustomUser
from .serializers import (
    KakaoSignInSerializer,
    SignInSerializer,
    SignUpSerializer,
    UserProfileImageSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class SignUpAPIView(APIView):
    serializer_class = SignUpSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"message": "Successfully Sign Up"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailCheckAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = CustomUser.objects.filter(email=email).exists()
        if not user:
            return Response(
                data={
                    "message": "사용 가능한 이메일 주소 입니다."
                },
                status=status.HTTP_200_OK
            )
        return Response(
            data={
                "message": "중복된 이메일 주소 입니다."
            },
            status=status.HTTP_409_CONFLICT
        )


class SignInAPIView(TokenObtainPairView):
    serializer_class = SignInSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data["refresh"]
        access_token = response.data["access"]

        email = request.data.get("email")
        user = CustomUser.objects.filter(email=email).first()
        serializer = UserSerializer(user)
        return Response(
            {
                "message": "Successfully Sign In",
                "user": serializer.data,
                "access": access_token,
                "refresh": refresh_token,
            },
            status=status.HTTP_200_OK,
        )


class SignOutAPIView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                raise AuthenticationFailed("No refresh token provided")

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(
            data={"message": "Successfully Read User Information", "user": serializer.data}, status=status.HTTP_200_OK
        )

    def put(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={"message": "Successfully Update User Information", "user": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(data={"message": "Successfully Delete User Information"}, status=status.HTTP_200_OK)


class KakaoSignInView(APIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        authorization_code = request.data.get("code")

        url = "https://kauth.kakao.com/oauth/token"
        headers = {"Content-type": "application/x-www-form-urlencoded;charset=utf-8"}
        data = {
            "grant_type": "authorization_code",
            "client_id": env("KAKAO_REST_API_KEY"),
            "redirect_uri": env("KAKAO_REDIRECT_URI"),
            "code": authorization_code,
        }
        token_response = requests.post(url, headers=headers, data=data)
        token_response_json = token_response.json()
        access_token = token_response_json.get("access_token")

        if not access_token:
            return Response(data={"message": "엑세스 토큰이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        headers = {"Authorization": f"Bearer {access_token}"}
        url = "https://kapi.kakao.com/v2/user/me"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response(
                data={"message": "카카오 계정 정보를 불러오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        user_info = response.json()

        email = user_info.get("kakao_account").get("email")
        user = CustomUser.objects.filter(email=email).first()

        if not user:
            user = CustomUser.objects.create(
                email=email, nickname=user_info.get("properties").get("nickname"), is_social=True
            )
            user.set_unusable_password()
            user.save()

        token = KakaoSignInSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        serializer = self.serializer_class(user)

        return Response(
            data={
                "message": "Successfully Sign In",
                "user": serializer.data,
                "access": access_token,
                "refresh": refresh_token,
            },
            status=status.HTTP_200_OK,
        )


class TokenRefreshView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                raise AuthenticationFailed("No refresh token provided")

            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            return Response(data={"access": access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileImageView(APIView):
    serializer_class = UserProfileImageSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        image_file = request.FILES.get('profile_image')
        if not image_file:
            return Response(
                data={
                    "message": "이미지 파일이 제공되지 않았습니다."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        file_size = image_file.size
        max_size_mb = 10
        max_size_bytes = max_size_mb * 1024 * 1024

        if file_size > max_size_bytes:
            return Response(
                data={
                    "message": "이 파일의 크기는 10MB를 초과합니다."
                },
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )

        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"message": "Successfully Profile Image Upload"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
