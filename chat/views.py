from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from .models import ChatRoom, ChatMessage, ChatMessageFile
from .serializers import (
    ChatRoomSerializer,
    ChatMessageSerializer,
    ChatMessageFileSerializer,
    ChatRoomNameUpdateSerializer
)


class IsParticipant(permissions.BasePermission):
    """
    채팅방 참가자 인지 확인 하는 권한 클래스
    """

    def has_object_permission(self, request, view, obj):
        return request.user in obj.participant.all()


class ChatRoomRetrieveAPIView(generics.RetrieveAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    # permission_classes = [IsParticipant]

    def get_object(self):
        obj = super().get_object()
        if not obj.name:
            participant_names = [str(user) for user in obj.participant.all()]
            obj.name = ', '.join(participant_names)
        return obj


# 나중에 유저 모델이 완성 되 면 이 부분 을 수정 하여 유저 네임 으로 채킹방 이름을 사용 하도록 지정 하자
class ChatRoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    # permission_classes = [IsParticipant]

    def get_queryset(self):
        queryset = super().get_queryset()
        for chat_room in queryset:
            if not chat_room.name:
                chat_room.name = ', '.join([str(user) for user in chat_room.participant.all()])
        return queryset



class ChatRoomNameRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomNameUpdateSerializer
    # permission_classes = [IsParticipant]


class ChatMessageCreateAPIView(generics.CreateAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    # permission_classes = [IsParticipant]


class ChatMessageDeleteAPIView(generics.DestroyAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    # permission_classes = [IsParticipant]


class ChatMessageFileListCreateAPIView(generics.ListCreateAPIView):
    queryset = ChatMessageFile.objects.all()
    serializer_class = ChatMessageFileSerializer
    # permission_classes = [IsParticipant]


from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
class LeaveChatRoomAPIView(APIView):
    """
    사용자를 채팅방에서 나가게 하는 API 뷰
    """

    def delete(self, request, chatroom_id, participant_id):
        try:
            chat_room = ChatRoom.objects.get(pk=chatroom_id)
            participant = User.objects.get(pk=participant_id)

            if participant in chat_room.participant.all():
                chat_room.participant.remove(participant)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "해당 사용자가 채팅방에 속해있지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        except ChatRoom.DoesNotExist:
            return Response({"error": "해당 ID를 가진 채팅방이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "해당 ID를 가진 사용자가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

# class LeaveChatRoomAPIView(generics.DestroyAPIView):
#     """
#     사용자 를 채팅방 에서 나가게 하는 API 뷰
#     """
#     queryset = ChatRoom.objects.all()
#     serializer_class = ChatRoomSerializer
#     # permission_classes = [IsParticipant]
#
#     def delete(self, request, *args, **kwargs):
#         chat_room_id = kwargs.get('chatroom_id')
#         try:
#             chat_room = self.get_object()
#             user = request.user
#             if user in chat_room.participants.all():
#                 chat_room.participants.remove(user)
#                 return Response(status=status.HTTP_204_NO_CONTENT)
#             else:
#                 return Response({"error": "사용자 가 해당 채팅방 에 속 해있지 않 습니다."}, status=status.HTTP_400_BAD_REQUEST)
#         except ChatRoom.DoesNotExist:
#             return Response({"error": "채팅방 을 찾을 수 없 습니다."}, status=status.HTTP_404_NOT_FOUND)
