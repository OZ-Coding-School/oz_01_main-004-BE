from rest_framework import serializers

from recipes.serializers import RecipeSerializer
from users.serializers import UserSerializer

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "content", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        recipe = request.data.get("recipe")
        validated_data["user"] = user
        validated_data["recipe"] = recipe
        return Comment.objects.create(**validated_data)
