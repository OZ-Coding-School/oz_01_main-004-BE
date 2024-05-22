from django.urls import path
from .views import CommentListCreateAPIView, CommentDetailAPIView

urlpatterns = [
    path('list/<int:recipe_id>/', CommentListCreateAPIView.as_view(), name='comment_list_create'),
    path('detail/<int:comment_id>/', CommentDetailAPIView.as_view(), name='comment_detail'),
]
