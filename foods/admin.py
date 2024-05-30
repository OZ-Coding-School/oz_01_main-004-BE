from django.contrib import admin

from foods.models import FoodIngredient, FoodType


@admin.register(FoodType)
class FoodTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "food_type_name",
        "food_type_image",
    )


@admin.register(FoodIngredient)
class FoodIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "food_ingredient_name",
        "food_ingredient_image",
    )
