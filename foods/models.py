from django.db import models

from common.models import Common


class FoodType(Common):
    food_type_image = models.ImageField(upload_to="food/types/")
    food_type_name = models.CharField(max_length=100)

    def __str__(self):
        return self.food_type_name


class FoodIngredient(Common):
    food_ingredient_image = models.ImageField(upload_to="food/ingredients/")
    food_ingredient_name = models.CharField(max_length=100)

    def __str__(self):
        return self.food_ingredient_name
