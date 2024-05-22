from django.urls import path
from .views import CommentListCreateAPIView, CommentDetailAPIView, RecipeCommentListAPIView

urlpatterns = [
    path('<int:recipe_id>/', CommentListCreateAPIView.as_view(), name='comment_list_create'),
    path('detail/<int:comment_id>/', CommentDetailAPIView.as_view(), name='comment_detail'),
    path('recipe/<int:recipe_id>/', RecipeCommentListAPIView.as_view(), name='post_comment_list'),
]
