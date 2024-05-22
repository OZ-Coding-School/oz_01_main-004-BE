from django.db import models

from common.models import Common
from foods.models import FoodIngredient, FoodType
from users.models import CustomUser


class Recipe(Common):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    food_type = models.ForeignKey(FoodType, on_delete=models.CASCADE)
    food_ingredient = models.ForeignKey(FoodIngredient, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    thumbnail = models.ImageField(upload_to="recipe/thumbnail/", null=True, blank=True)
    level = models.CharField(max_length=100)

    def __str__(self):
        return self.title
