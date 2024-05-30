import json
import logging

import aiohttp
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from .models import ChatFile, ChatMessage  # 모델 이름은 적절하게 수정하세요
from .serializers import (  # 시리얼라이저 이름은 적절하게 수정하세요
    ChatFileSerializer,
    ChatMessageSerializer,
    UserChatSerializer,
)

logger = logging.getLogger(__name__)

# 메시지 읽음 상태를 저장하는 데이터 구조
read_status = {}


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        logger.info(f"Connecting to room {self.room_group_name}")

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"Disconnected from room {self.room_group_name}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type")

        if message_type == "text":
            await self.handle_text_message(text_data_json)
        elif message_type == "file":
            await self.handle_file_message(text_data_json)
        elif message_type == "read":
            await self.handle_read_message(text_data_json)

    async def handle_text_message(self, data):
        room_id = data["room"]
        sender_id = data["sender"]
        content = data["content"]

        logger.info(f"Handling text message: {data}")

        # API 호출을 통해 메시지 생성
        async with aiohttp.ClientSession() as session:
            api_url = f"{settings.API_BASE_URL}api/v1/chat/chatmessages/"
            payload = {"room": room_id, "sender": sender_id, "content": content}
            headers = {"Content-Type": "application/json"}
            logger.info(f"Sending request to {api_url} with payload {payload} and headers {headers}")

            try:
                async with session.post(api_url, json=payload, headers=headers) as response:
                    logger.info(f"Received response status: {response.status}")
                    response_data = await response.json()
                    logger.info(f"API response: {response_data}")

                    if response.status == 200 or response.status == 201:
                        # 생성된 메시지의 내용을 클라이언트에게 보냄
                        await self.send(
                            text_data=json.dumps(
                                {
                                    "type": "text",
                                    "message": response_data,
                                    "read_by": [],  # 초기에는 아무도 읽지 않았음을 나타내는 빈 리스트
                                }
                            )
                        )

                        # 그룹에 메시지 보내기
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "chat_message",
                                "message": response_data,
                            },
                        )
                    else:
                        logger.error(f"Unexpected response status: {response.status}")
            except Exception as e:
                logger.error(f"Error during API request: {e}")

    async def handle_file_message(self, data):
        room_id = data["room"]
        sender_id = data["sender"]
        file_url = data["file_url"]

        logger.info(f"Handling file message: {data}")

        # API 호출을 통해 메시지 생성
        async with aiohttp.ClientSession() as session:
            api_url = f"{settings.API_BASE_URL}api/v1//cahtfiles/"
            payload = {"room": room_id, "sender": sender_id, "file_url": file_url}
            headers = {"Content-Type": "application/json"}
            logger.info(f"Sending request to {api_url} with payload {payload} and headers {headers}")

            try:
                async with session.post(api_url, json=payload, headers=headers) as response:
                    logger.info(f"Received response status: {response.status}")
                    response_data = await response.json()
                    logger.info(f"API response: {response_data}")

                    if response.status == 200 or response.status == 201:
                        # 생성된 파일 메시지의 내용을 클라이언트에게 보냄
                        await self.send(
                            text_data=json.dumps(
                                {
                                    "type": "file",
                                    "file": response_data,
                                    "read_by": [],  # 초기에는 아무도 읽지 않았음을 나타내는 빈 리스트
                                }
                            )
                        )

                        # 그룹에 메시지 보내기
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "chat_file",
                                "file": response_data,
                            },
                        )
                    else:
                        logger.error(f"Unexpected response status: {response.status}")
            except Exception as e:
                logger.error(f"Error during API request: {e}")

    async def handle_read_message(self, data):
        message_id = data["message_id"]
        user_id = data["user_id"]

        if message_id in read_status:
            read_status[message_id].append(user_id)
        else:
            read_status[message_id] = [user_id]

        await self.send(
            text_data=json.dumps({"type": "read", "message_id": message_id, "read_by": read_status[message_id]})
        )

    async def chat_message(self, event):
        message = event["message"]

        # 클라이언트에 메시지와 유저 정보를 전송
        await self.send(
            text_data=json.dumps(
                {
                    "type": "text",
                    "message": message,
                }
            )
        )

    async def chat_file(self, event):
        file = event["file"]

        # 클라이언트에 파일 메시지와 유저 정보를 전송
        await self.send(
            text_data=json.dumps(
                {
                    "type": "file",
                    "file": file,
                }
            )
        )

    @database_sync_to_async
    def get_chat_message(self, message_id):
        return ChatMessage.objects.get(id=message_id)

    @database_sync_to_async
    def get_chat_file(self, message_id):
        return ChatFile.objects.get(id=message_id)
