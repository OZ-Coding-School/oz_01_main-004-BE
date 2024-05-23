from rest_framework import serializers

from comments.models import Comment
from favorite.models import Favorite
from foods.models import FoodIngredient, FoodType
from foods.serializers import FoodIngredientSerializer, FoodTypeSerializer
from users.serializers import UserSerializer

from .models import Recipe, RecipeImage


class RecipeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    food_type = FoodTypeSerializer(read_only=True)
    food_ingredient = FoodIngredientSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "content",
            "thumbnail",
            "user",
            "food_type",
            "food_ingredient",
            "level",
            "is_favorite",
            "favorites_count",
            "comments_count",
            "created_at",
            "updated_at",
        ]
        depth = 1

    def create(self, validated_data):
        request = self.context.get("request")
        food_type_id = int(request.data.get("food_type"))
        food_ingredient_id = int(request.data.get("food_ingredient"))
        validated_data["user"] = request.user
        validated_data["food_type"] = FoodType.objects.filter(pk=food_type_id).first()
        validated_data["food_ingredient"] = FoodIngredient.objects.filter(pk=food_ingredient_id).first()
        return Recipe.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("title", "") != "":
            instance.title = validated_data.get("title")
        if validated_data.get("content", "") != "":
            instance.content = validated_data.get("content")
        if validated_data.get("thumbnail", "") != "":
            instance.thumbnail = validated_data.get("thumbnail")
        if validated_data.get("level", "") != "":
            instance.level = validated_data.get("level")

        request = self.context.get("request")
        if request.data.get("food_type", "") != "":
            food_type_id = int(request.data.get("food_type"))
            instance.food_type = FoodType.objects.filter(pk=food_type_id).first()
        if request.data.get("food_ingredient", "") != "":
            food_ingredient_id = int(request.data.get("food_ingredient"))
            instance.food_ingredient = FoodIngredient.objects.filter(pk=food_ingredient_id).first()

        instance.save()
        return instance

    def get_comments_count(self, obj):
        return Comment.objects.filter(recipe=obj).count()

    def get_favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    def get_is_favorite(self, obj):
        request = self.context.get("request")
        user = request.user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False


class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeImage
        fields = ["image"]

    def create(self, validated_data):
        image = validated_data.get("image")
        # recipe_id = self.context.get("recipe_id")
        # validated_data["image"] = str(recipe_id) + image
        return RecipeImage.objects.create(**validated_data)
