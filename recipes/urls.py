from django.urls import path

from recipes import views


urlpatterns = [
    path('list/', views.RecipeListAPIView.as_view(), name="recipe_list"),
    path('detail/<int:recipe_id>/', views.RecipeDetailAPIView.as_view(), name="recipe_detail"),
]
