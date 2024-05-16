from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
import pytest
import json
import asyncio
from chat.consumers import ChatConsumer
from chat.models import ChatMessage, ChatRoom
from django.contrib.auth.models import User

from asgiref.testing import ApplicationCommunicator
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
import asyncio
import json
import pytest

# 테스트용 사용자 생성 함수 (비동기)
@database_sync_to_async
def create_test_user(username):
    user = User.objects.create(username=username)  # 유저 생성
    return user.id  # 생성된 유저의 id 반환

# 테스트용 메시지 생성 함수 (비동기)
# @database_sync_to_async
# def create_test_message(message_content, sender, room):
#     return ChatMessage.objects.create(content=message_content, sender=sender, room=room)

# 테스트용 메시지 생성 함수 (비동기)
# @database_sync_to_async
async def create_test_message(message_content, sender_id, room_id):
    sender = await database_sync_to_async(User.objects.filter(id=sender_id).first)()
    room = await database_sync_to_async(ChatRoom.objects.filter(id=room_id).first)()
    return ChatMessage.objects.create(content=message_content, sender=sender, room=room)

@pytest.mark.asyncio
async def test_chat_consumer():
    # 테스트용 사용자 생성
    sender_id = await create_test_user("test_user")

    # 테스트용 메시지 생성
    room_id = 1  # 테스트용 채팅방 ID
    message_content = "Test message"
    await create_test_message(message_content, sender_id, room_id)

    # 웹소켓 통신을 위한 communicator 설정
    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), f"ap1/v1/chat/ws/chatrooms/{room_id}/")
    connected, _ = await communicator.connect()
    assert connected

    # 데이터베이스에 저장된 메시지가 클라이언트로 전송되는지 확인
    response = await communicator.receive_json_from()
    assert response['messages'][0]['message'] == message_content

    await communicator.disconnect()