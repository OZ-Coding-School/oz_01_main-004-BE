from operator import attrgetter

from django.db.models import F, Max, Prefetch
from django.db.models.functions import Coalesce
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser

from .models import ChatFile, ChatMessage, ChatRoom
from .serializers import (
    ChatFileSerializer,
    ChatMessageSerializer,
    ChatRoomDetailSerializer,
    ChatRoomNameUpdateSerializer,
    ChatRoomSerializer,
)


class MyPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = "page_size"


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
    queryset = ChatRoom.objects.all().prefetch_related(
        Prefetch("participant", queryset=CustomUser.objects.only("id", "nickname", "email", "profile_image")),
        Prefetch("messages"),
        Prefetch("files"),
    )
    serializer_class = ChatRoomDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    pagination_class = MyPagination  # 사용자 정의 페이지네이션 클래스를 설정합니다.

    def get_paginated_messages(self, messages):
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(messages, self.request)
        if page is not None:
            return paginator.get_paginated_response(page).data
        return messages

    def get_object(self):
        obj = super().get_object()
        if not obj.name:
            participant_names = [
                user.nickname for user in obj.participant.all() if user != self.request.user
            ]  # 현재 사용자를 제외한 다른 사용자의 닉네임만 필터링합니다.
            obj.name = ", ".join(participant_names)
        return obj

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # 시리얼라이저에서 정렬된 메시지를 가져옴
        sorted_messages = serializer.get_messages(instance)

        # 페이지네이션 적용
        paginated_messages = self.get_paginated_messages(sorted_messages)

        return Response({**serializer.data, "messages": paginated_messages})


# 나중에 유저 모델이 완성 되 면 이 부분 을 수정 하여 유저 네임 으로 채킹방 이름을 사용 하도록 지정 하자
class ChatRoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all().prefetch_related(
        Prefetch("participant", queryset=CustomUser.objects.only("id", "nickname", "email", "profile_image"))
    )
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        user = self.request.user

        # 최신 메시지 및 파일 생성 시간을 가져옵니다.
        queryset = ChatRoom.objects.filter(participant=user).annotate(
            latest_message_time=Coalesce(Max("messages__created_at"), F("created_at")),
            latest_file_time=Coalesce(Max("files__created_at"), F("created_at")),
        )

        # 최신 데이터를 비교하여 정렬합니다.
        queryset = sorted(
            queryset,
            key=lambda x: (
                max(x.latest_message_time, x.latest_file_time)
                if (x.latest_message_time or x.latest_file_time)
                else x.created_at
            ),
            reverse=True,
        )

        # 채팅방 이름이 없는 경우, 참가자들의 이름으로 채팅방 이름 설정
        for chat_room in queryset:
            if not chat_room.name:
                chat_room.name = ", ".join(
                    [user.nickname for user in chat_room.participant.all() if user != self.request.user]
                )

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        participants_data = self.request.data.get("participant", [])  # 요청에서 참가자 목록 가져오기
        participants_data.append(user.id)  # 현재 사용자도 참가자에 추가

        # 채팅방 생성
        chat_room = serializer.save()

        # 참가자 추가
        for participant_id in participants_data:
            participant = CustomUser.objects.get(id=participant_id)
            chat_room.participant.add(participant)


class ChatRoomNameRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomNameUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]


class ChatMessageCreateAPIView(generics.CreateAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    # permission_classes = [permissions.IsAuthenticated, IsSender]

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
    # permission_classes = [permissions.IsAuthenticated, IsSender]

    def create(self, request, *args, **kwargs):
        # 채팅방 ID 가져오기
        chatroom_id = request.data.get("room")
        sender_id = request.data.get("sender")
        message_file = request.FILES.get("file_url")  # 파일 객체 가져오기
        file_name = message_file.name  # 파일 이름 가져오기

        # 채팅방 객체 가져오기
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": "채팅방을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 채팅방의 참가자 목록에서 작성자 찾기
        if int(sender_id) not in chatroom.participant.values_list("id", flat=True):
            return Response(
                {"error": "채팅방에 참가하지 않은 유저는 파일메시지를 작성할 수 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)

        # # ChatFileSerializer를 사용하여 데이터 생성
        # serializer = ChatFileSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def get(self, request, *args, **kwargs):
    #     # 최근에 생성된 ChatFile 모델의 객체를 가져와서 시리얼라이즈
    #     queryset = ChatFile.objects.filter(sender=request.user).order_by('-created_at')[:1]
    #     serializer = ChatFileSerializer(queryset, many=True)
    #     return Response(serializer.data)


class ChatFileDeleteAPIView(generics.DestroyAPIView):
    queryset = ChatFile.objects.all()
    serializer_class = ChatFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsSender]



class LeaveChatRoomAPIView(APIView):
    """
    사용자를 채팅방에서 나가게 하는 API 뷰
    """

    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def delete(self, request, chatroom_id, participant_id):
        try:
            chat_room = ChatRoom.objects.get(pk=chatroom_id)
            participant = CustomUser.objects.get(pk=participant_id)

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
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "해당 ID를 가진 사용자가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
