from django.urls import path

from recipes import views

urlpatterns = [
    path("main/", views.RecipeMainAPIView.as_view(), name="main_recipe_list"),
    path("list/", views.RecipeListAPIView.as_view(), name="recipe_list"),
    path("my/", views.RecipeMyAPIView.as_view(), name="my_recipe_list"),
    path("detail/<int:recipe_id>/", views.RecipeDetailAPIView.as_view(), name="recipe_detail"),
    path("image-upload/<int:recipe_id>/", views.RecipeImageAPIView.as_view(), name="recipe_image_upload"),
]
