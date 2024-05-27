from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Recipe, RecipeImage
from .serializers import RecipeImageSerializer, RecipeSerializer
import uuid


class RecipePagination(PageNumberPagination):
    page_size = 16
    page_size_query_param = "page_size"
    max_page_size = 100


class RecipeMyPagePagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 100


class RecipeMainAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RecipeSerializer

    def get(self, request):
        popular_recipes = Recipe.objects.annotate(favorites_count=Count("favorite")).order_by("-favorites_count")[:4]
        recently_recipes = Recipe.objects.all().order_by("-created_at")[:4]

        popular_serializer = self.serializer_class(popular_recipes, many=True, context={"request": request})
        recently_serializer = self.serializer_class(recently_recipes, many=True, context={"request": request})

        return Response(
            data={
                "message": "Successfully Read Main Recipe List",
                "popular_recipe_list": popular_serializer.data,
                "recently_recipe_list": recently_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class RecipeListAPIView(APIView):
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    @staticmethod
    def get_list(request):
        recipes = Recipe.objects.all().order_by("-created_at")

        search = request.query_params.get("search")
        if search:
            recipes = recipes.filter(Q(title__icontains=search) | Q(content__icontains=search))

        food_type = request.query_params.get("food_type")
        if food_type:
            recipes = recipes.filter(food_type=food_type)

        food_ingredient = request.query_params.get("food_ingredient")
        if food_ingredient:
            recipes = recipes.filter(food_ingredient=food_ingredient)

        level = request.query_params.get("level")
        if level:
            recipes = recipes.filter(level=level)

        return recipes

    def get(self, request):
        recipes = self.get_list(request)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(recipes, request)
        if not page:
            serializer = self.serializer_class(recipes, many=True, context={"request": request})
            return Response(
                data={"message": "Successfully Read Recipe List", "recipe_list": serializer.data},
                status=status.HTTP_200_OK,
            )
        serializer = RecipeSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        uuid_list = data.pop("uuid_list", [])
        valid_uuid_list = get_uuid_list(uuid_list)
        serializer = self.serializer_class(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        recipe_id = serializer.data.get("id")
        for uuid_data in valid_uuid_list:
            image = RecipeImage.objects.filter(image_uuid=uuid_data).first()
            image.recipe_id = recipe_id
            image.save()
        return Response(
            data={
                "message": "Successfully Created Recipe.",
                "recipe": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class RecipeMyAPIView(APIView):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = RecipeMyPagePagination

    def get(self, request):
        user = request.user
        my_recipes = Recipe.objects.filter(user_id=user.id).order_by("-created_at")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(my_recipes, request)
        if not page:
            serializer = self.serializer_class(my_recipes, many=True, context={"request": request})
            return Response(
                data={"message": "Successfully Read My Recipe List", "my_recipe_list": serializer.data},
                status=status.HTTP_200_OK,
            )
        serializer = RecipeSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class RecipeDetailAPIView(APIView):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, recipe_id):
        recipe = Recipe.objects.filter(pk=recipe_id).first()
        serializer = self.serializer_class(recipe, context={"request": request})
        return Response(
            data={"message": "Successfully Read Recipe Detail", "recipe": serializer.data}, status=status.HTTP_200_OK
        )

    def put(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id, user_id=request.user.id)
        serializer = self.serializer_class(recipe, data=request.data, context={"request": request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data={"message": "Successfully Updated Recipe.", "recipe": serializer.data}, status=status.HTTP_200_OK
        )

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id, user_id=request.user.id)
        recipe.delete()
        return Response(data={"message": "Successfully Deleted Recipe."}, status=status.HTTP_200_OK)


class RecipeImageAPIView(APIView):
    serializer_class = RecipeImageSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={"message": "Successfully Updated Recipe Image", "image_info": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            data={
                "message": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


def get_uuid_list(uuid_list_str):
    uuid_list = [s.strip().strip('"') for s in uuid_list_str]
    valid_uuid_list = []
    for u in uuid_list:
        try:
            val = uuid.UUID(u, version=4)
            valid_uuid_list.append(str(val))
        except ValueError:
            pass
    return valid_uuid_list
