from django.db import models
from common.models import Common
from users.models import CustomUser
from recipes.models import Recipe


class Comment(Common):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.content
