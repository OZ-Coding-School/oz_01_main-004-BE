from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import ChatFile, ChatMessage, ChatRoom
from .serializers import (
    ChatFileSerializer,
    ChatMessageSerializer,
    ChatRoomDetailSerializer,
    ChatRoomNameUpdateSerializer,
    ChatRoomSerializer,
)


class IsParticipant(permissions.BasePermission):
    """
    채팅방 참가자 인지 확인 하는 권한 클래스
    """

    def has_object_permission(self, request, view, obj):
        return request.user in obj.participant.all()


class IsSender(permissions.BasePermission):
    """
    작성자가 유저 본인인지 확인하는 클래스
    """

    def has_object_permission(self, request, view, obj):
        return request.user == obj.sender.all()


class ChatRoomRetrieveAPIView(generics.RetrieveAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_object(self):
        obj = super().get_object()
        if not obj.name:
            participant_names = [str(user) for user in obj.participant.all()]
            obj.name = ", ".join(participant_names)
        return obj


# 나중에 유저 모델이 완성 되 면 이 부분 을 수정 하여 유저 네임 으로 채킹방 이름을 사용 하도록 지정 하자
class ChatRoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 참여한 채팅방만 필터링
        queryset = queryset.filter(participant=user)
        # 채팅방 이름이 없는 경우, 참가자들의 이름으로 채팅방 이름 설정
        for chat_room in queryset:
            if not chat_room.name:
                chat_room.name = ", ".join([str(user) for user in chat_room.participant.all()])
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        participants = self.request.data.get("participant", [])  # 요청에서 참가자 목록 가져오기
        participants.append(user.id)  # 현재 사용자도 참가자에 추가
        serializer.save(participant=participants)  # 새로운 채팅방을 생성할 때 참가자 설정


class ChatRoomNameRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomNameUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]


class ChatMessageCreateAPIView(generics.CreateAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsSender]

    def create(self, request, *args, **kwargs):
        # 채팅방 ID 가져오기
        chatroom_id = request.data.get("room")
        sender_id = request.data.get("sender")
        message_content = request.data.get("content")

        # 채팅방 객체 가져오기
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": "채팅방을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 채팅방의 참가자 목록에서 작성자 찾기
        if sender_id not in chatroom.participant.values_list("id", flat=True):
            return Response(
                {"error": "채팅방에 참가하지 않은 유저는 메시지를 작성할 수 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)


class ChatMessageDeleteAPIView(generics.DestroyAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsSender]


class ChatFileCreateAPIView(generics.CreateAPIView):
    queryset = ChatFile.objects.all()
    serializer_class = ChatFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsSender]

    def create(self, request, *args, **kwargs):
        # 채팅방 ID 가져오기
        chatroom_id = request.data.get("room")
        sender_id = request.data.get("sender")
        message_file = request.data.get("file")

        # 채팅방 객체 가져오기
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": "채팅방을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 채팅방의 참가자 목록에서 작성자 찾기
        if sender_id not in chatroom.participant.values_list("id", flat=True):
            return Response(
                {"error": "채팅방에 참가하지 않은 유저는 파일메시지를 작성할 수 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)


class ChatFileDeleteAPIView(generics.DestroyAPIView):
    queryset = ChatFile.objects.all()
    serializer_class = ChatFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsSender]


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
                return Response(
                    {"error": "해당 사용자가 채팅방에 속해있지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ChatRoom.DoesNotExist:
            return Response(
                {"error": "해당 ID를 가진 채팅방이 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "해당 ID를 가진 사용자가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
