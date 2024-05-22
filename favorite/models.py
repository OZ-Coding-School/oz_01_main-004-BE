from django.db import models
from common.models import Common
from users.models import CustomUser
from recipes.models import Recipe


class Favorite(Common):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
