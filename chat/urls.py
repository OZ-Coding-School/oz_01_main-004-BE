from django.urls import path

from .views import (
    ChatFileCreateAPIView,
    ChatFileDeleteAPIView,
    ChatMessageCreateAPIView,
    ChatMessageDeleteAPIView,
    ChatRoomListCreateAPIView,
    ChatRoomNameRetrieveUpdateAPIView,
    ChatRoomRetrieveAPIView,
    LeaveChatRoomAPIView,
)

urlpatterns = [
    # 채팅방 생성/불러오기
    path("chatrooms", ChatRoomListCreateAPIView.as_view(), name="chatroom-list"),
    # 특정 채팅방 블러오기
    path("chatrooms/<int:pk>", ChatRoomRetrieveAPIView.as_view(), name="chatroom-detail"),
    # 채팅메시지 생성
    path("chatmessages", ChatMessageCreateAPIView.as_view(), name="chatmessage-create"),
    # 채팅메시지 삭제
    path(
        "chatmessages/<int:pk>",
        ChatMessageDeleteAPIView.as_view(),
        name="chatmessage-delete",
    ),
    # 채팅 파일메시지(이미지,동영상 등등) 생성
    path(
        "chatfiles",
        ChatFileCreateAPIView.as_view(),
        name="chatmessagefile-list",
    ),
    # 채팅 파일메세시지 삭제
    path(
        "chatfiles/<int:pk>",
        ChatFileDeleteAPIView.as_view(),
        name="chatmessage-delete",
    ),
    # 특정 채팅방 이름 수정
    path(
        "chatrooms/<int:pk>/name",
        ChatRoomNameRetrieveUpdateAPIView.as_view(),
        name="chatroom-name-update",
    ),
    # 채팅방 나가기(유저한테서 권한 삭제)
    path(
        "chatrooms/<int:chatroom_id>/leave/<int:participant_id>",
        LeaveChatRoomAPIView.as_view(),
        name="leave-chatroom",
    ),
]
