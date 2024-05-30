from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Recipe

from .models import Favorite
from .serializers import FavoriteSerializer


class FavoriteRecipePagePagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100


class FavoriteListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteSerializer
    pagination_class = FavoriteRecipePagePagination

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(favorites, request)
        if not page:
            serializer = self.serializer_class(favorites, many=True, context={"request": request})
            return Response(
                data={"favorite_list": serializer.data},
                status=status.HTTP_200_OK,
            )
        serializer = self.serializer_class(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class FavoriteDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteSerializer

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if recipe.user == request.user:
            return Response(
                data={"message": "내가 작성한 게시물은 찜할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        request.data["recipe"] = recipe
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    data={
                        "message": "Successfully Created Favorite",
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError:
                return Response(data={"message": "이미 찜한 게시물 입니다."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        favorite = get_object_or_404(Favorite, recipe_id=recipe_id, user_id=request.user.id)
        favorite.delete()
        return Response(data={"message": "Successfully Deleted Favorite"}, status=status.HTTP_200_OK)
