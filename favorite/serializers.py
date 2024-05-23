from rest_framework import serializers

from favorite.models import Favorite
from recipes.serializers import RecipeSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "recipe"]
        depth = 1

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        validated_data["user"] = user
        validated_data["recipe"] = request.data.get("recipe")
        return Favorite.objects.create(**validated_data)
