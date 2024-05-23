from django.db import models

from common.models import Common
from recipes.models import Recipe
from users.models import CustomUser


class Favorite(Common):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "recipe")
