from rest_framework import serializers

from foods.models import FoodIngredient, FoodType


class FoodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodType
        fields = "__all__"


class FoodIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodIngredient
        fields = "__all__"
