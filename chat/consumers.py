import aiohttp
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatFile,ChatRoom
from rest_framework import status
from django.conf import settings


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'text':
            await self.handle_text_message(text_data_json)
        elif message_type == 'file':
            await self.handle_file_message(text_data_json)

    async def handle_text_message(self, data):
        room_id = data['room']
        sender_id = data['sender']
        content = data['content']

        # API 호출을 통해 메시지 저장
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f'{settings.API_BASE_URL}/api/v1/chat/chatmessages/',
                    json={
                        'room': room_id,
                        'sender': sender_id,
                        'content': content
                    }
            ) as response:
                status_code = response.status
                if status_code == status.HTTP_404_NOT_FOUND:
                    await self.send(text_data=json.dumps({'error': '없는 채팅방입니다.'}))
                elif status_code == status.HTTP_403_FORBIDDEN:
                    await self.send(text_data=json.dumps({'error': '채팅방에 참가자가 아닙니다.'}))
                elif status_code == status.HTTP_201_CREATED:
                    # 메시지 전송
                    await self.send(text_data=json.dumps({'content': content}))

                    # 그룹에 메시지 보내기
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': content
                        }
                    )

    async def handle_file_message(self, data):
        room_id = data['room']
        sender_id = data['sender']
        file_url = data['file_url']

        # API 호출을 통해 파일 메시지 저장
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f'{settings.API_BASE_URL}/api/v1/chat/chatfiles/',
                    json={
                        'room': room_id,
                        'sender': sender_id,
                        'file_url': file_url
                    }
            ) as response:
                status_code = response.status
                if status_code == status.HTTP_404_NOT_FOUND:
                    await self.send(text_data=json.dumps({'error': '없는 채팅방입니다.'}))
                elif status_code == status.HTTP_403_FORBIDDEN:
                    await self.send(text_data=json.dumps({'error': '채팅방에 참가자가 아닙니다.'}))
                elif status_code == status.HTTP_201_CREATED:
                    # 파일 메시지 전송
                    await self.send(text_data=json.dumps({'file_url': file_url}))

                    # 그룹에 파일 메시지 보내기
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'file_message',
                            'file_url': file_url
                        }
                    )

    async def chat_message(self, event):
        # 채팅 메시지를 받아서 클라이언트로 전송
        await self.send(text_data=json.dumps({
            'content': event['message']
        }))

    async def file_message(self, event):
        # 파일 메시지를 받아서 클라이언트로 전송하는 메서드
        user_id = self.scope["user"].id
        latest_file = await self.get_latest_file_data(user_id)
        if latest_file:
            file_url = latest_file.file_url
            await self.send(text_data=json.dumps({"file_url": file_url}))

    @sync_to_async
    def get_latest_file_data(self, user_id):
        # 데이터베이스에서 최신 파일 데이터를 가져오는 메서드
        latest_file = ChatFile.objects.filter(sender_id=user_id).order_by('-created_at').first()
        return latest_file
