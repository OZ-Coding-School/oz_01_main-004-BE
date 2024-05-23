from django.urls import path

from favorite import views

urlpatterns = [
    path("list/", views.FavoriteListAPIView.as_view(), name="favorite_list"),
    path("list/<int:recipe_id>/", views.FavoriteListAPIView.as_view(), name="favorite_list"),
    path("detail/<int:favorite_id>/", views.FavoriteDetailAPIView.as_view(), name="favorite_detail"),
]
