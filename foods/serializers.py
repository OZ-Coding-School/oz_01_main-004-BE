from rest_framework import serializers

from foods.models import FoodIngredient, FoodType


class FoodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodType
        fields = ["id", "food_type_name", "food_type_image"]


class FoodIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodIngredient
        fields = ["id", "food_ingredient_name", "food_ingredient_image"]
