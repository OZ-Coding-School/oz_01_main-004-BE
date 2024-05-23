from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Recipe
from .models import Favorite
from .serializers import  FavoriteSerializer


class FavoriteListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteSerializer

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        serializer = self.serializer_class(favorites, many=True)
        return Response(
            data={
                "message": "Successfully Read Favorite list",
                "favorite_list": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def post(self, request, recipe_id):
        recipe = Recipe.objects.filter(pk=recipe_id).first()
        if not recipe:
            return Response(
                data={'message': 'Recipe Not Found'},
                status=status.HTTP_404_NOT_FOUND
            )
        if recipe.user == request.user:
            return Response(
                data={'message': '내가 작성한 게시물은 찜할 수 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.data["recipe"] = recipe
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response(
                    data={'message': '이미 찜한 게시물 입니다.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                data={
                    'message': 'Successfully Created Favorite'
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            data={
                "message": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class FavoriteDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, favorite_id):
        favorite = Favorite.objects.filter(pk=favorite_id).first()
        if not favorite:
            return Response(
                data={'message': 'Favorite Not Found'},
                status=status.HTTP_404_NOT_FOUND
            )
        favorite.delete()
        return Response(
            data={'message': 'Successfully Deleted Favorite'},
            status=status.HTTP_200_OK
        )
