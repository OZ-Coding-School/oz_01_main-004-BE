from rest_framework import generics, status

from foods.models import FoodIngredient, FoodType
from foods.serializers import FoodIngredientSerializer, FoodTypeSerializer


class FoodTypeList(generics.ListAPIView[FoodType]):
    queryset = FoodType.objects.all().order_by('id')
    serializer_class = FoodTypeSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {"message": "Successfully Read Food Type List", "food_type_list": response.data}
        response.status_code = status.HTTP_200_OK
        return response


class FoodIngredientList(generics.ListAPIView[FoodIngredient]):
    queryset = FoodIngredient.objects.all()
    serializer_class = FoodIngredientSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {"message": "Successfully Read Food Ingredient List", "food_ingredient_list": response.data}
        response.status_code = status.HTTP_200_OK
        return response
