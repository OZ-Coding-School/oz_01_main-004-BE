from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Recipe

from .models import Comment
from .serializers import CommentSerializer


class CommentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, recipe_id):
        comments = Comment.objects.filter(recipe_id=recipe_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(
            {"message": "Successfully Read Comments", "comment_list": serializer.data}, status=status.HTTP_200_OK
        )

    def post(self, request, recipe_id):
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            request.data["recipe"] = recipe
        except Recipe.DoesNotExist:
            raise NotFound("Recipe not found")

        serializer = CommentSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            if len(serializer.validated_data.get('content', '')) > 200:
                raise ValidationError("Content length exceeds the maximum allowed length of 200 characters.")

            serializer.save()
            return Response({"message": "Successfully Create Comment"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, comment_id):
        try:
            return Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            raise NotFound("Comment not found")

    def get(self, request, comment_id):
        comment = self.get_object(comment_id)
        serializer = CommentSerializer(comment)
        return Response({"message": "Successfully Read Comment", "comment": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, comment_id):
        comment = self.get_object(comment_id)
        if request.user != comment.user:
            raise PermissionDenied("You do not have permission to edit this comment")

        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Successfully Update Comment", "comment": serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        comment = self.get_object(comment_id)
        if request.user != comment.user:
            raise PermissionDenied("You do not have permission to delete this comment")

        comment.delete()
        return Response({"message": "Successfully Delete Comment"}, status=status.HTTP_200_OK)
