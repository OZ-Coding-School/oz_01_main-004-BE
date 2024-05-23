from rest_framework import serializers

from recipes.serializers import RecipeSerializer
from users.serializers import UserSerializer

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    # user = UserSerializer()
    # recipe = RecipeSerializer()

    class Meta:
        model = Comment
        fields = ["id", "user", "recipe", "content", "created_at", "updated_at"]
