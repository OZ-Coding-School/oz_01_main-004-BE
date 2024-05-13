from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "nickname", "password"]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class SignInSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise AuthenticationFailed("이메일과 비밀번호를 입력해주세요.")

        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("잘못된 이메일 또는 비밀번호입니다.")

        data["email"] = user.email
        data["user_id"] = user.id

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "nickname", "profile_image", "created_at", "updated_at"]


class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["profile_image"]
