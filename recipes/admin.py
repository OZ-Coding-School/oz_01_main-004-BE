from django.contrib import admin

from .models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "food_type",
        "food_ingredient",
        "title",
        "content",
        "thumbnail",
        "level",
    )
