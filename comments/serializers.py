from rest_framework import serializers
from .models import Comment
from users.serializers import UserSerializer
from recipes.serializers import RecipeSerializer

class CommentSerializer(serializers.ModelSerializer):
    # user = UserSerializer()
    # recipe = RecipeSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'recipe', 'content', 'created_at', 'updated_at']
