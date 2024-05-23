from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/foods/", include("foods.urls")),
    path("api/v1/recipes/", include("recipes.urls")),
    path("api/v1/favorite/", include("favorite.urls")),
    path("api/v1/chat/", include("chat.urls")),
    path("api/v1/comments/", include("comments.urls")),
]
# 미디어 파일에 대한 URL 패턴 추가
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
