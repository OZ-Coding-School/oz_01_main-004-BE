from django.urls import path

from foods import views

urlpatterns = [
    path("types/", views.FoodTypeList.as_view(), name="food-type-list"),
    path("ingredients/", views.FoodIngredientList.as_view(), name="food-ingredient-list"),
]
