import aiohttp
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatFile,ChatRoom
from rest_framework import status
from django.conf import settings


# 메시지 읽음 상태를 저장하는 데이터 구조
read_status = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

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

        # API 호출을 통해 메시지 생성
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f'{settings.API_BASE_URL}api/v1/chat/chatmessages/',
                    json={
                        'room': room_id,
                        'sender': sender_id,
                        'content': content
                    }
            ) as response:
                # apiview에서 처리하는 부분이기때문에 필요 없다.
                # status_code = response.status
                # if status_code == status.HTTP_404_NOT_FOUND:
                #     await self.send(text_data=json.dumps({'error': '없는 채팅방입니다.'}))
                # elif status_code == status.HTTP_403_FORBIDDEN:
                #     await self.send(text_data=json.dumps({'error': '채팅방에 참가자가 아닙니다.'}))
                # elif status_code == status.HTTP_201_CREATED:
                    # 생성된 메시지의 내용을 가져옴
                response_data = await response.json()
                message_content = response_data.get('content')
                message_id = response_data.get('id')

                # 생성된 메시지의 내용을 클라이언트에게 보냄
                await self.send(text_data=json.dumps({
                    'content': message_content,
                    'sender_id': sender_id,
                    'message_id': message_id,
                    'read_by': []  # 초기에는 아무도 읽지 않았음을 나타내는 빈 리스트
                }))

                # 그룹에 메시지 보내기
                await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'content': message_content,
                    'sender_id': sender_id,
                    'message_id': message_id
                }
            )


    async def handle_file_message(self, data):
        room_id = data['room']
        sender_id = data['sender']
        file_url = data['file_url']

        # API 호출을 통해 파일 메시지 저장
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f'{settings.API_BASE_URL}api/v1/chat/chatfiles/',
                    json={
                        'room': room_id,
                        'sender': sender_id,
                        'file_url': file_url
                    }
            ) as response:
                if response.status == status.HTTP_201_CREATED:
                    # 파일이 성공적으로 생성되었을 때, API 응답 데이터를 받음
                    file_data = await response.json()
                    file_id = file_data.get('id')

                    # 파일 메시지 전송
                    await self.send(text_data=json.dumps({
                        'content': file_url,
                        'sender_id': sender_id,
                        'file_id': file_id,
                        'read_by': []  # 초기에는 아무도 읽지 않았음을 나타내는 빈 리스트
                    }))

                    # 그룹에 파일 메시지 보내기
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'file_message',
                            'content': file_url,
                            'sender_id': sender_id,
                            'file_id': file_id
                        }
                    )
                else:
                    # 실패한 경우, 적절한 에러 메시지 전송
                    error_message = await response.text()
                    await self.send(text_data=json.dumps({'error': error_message}))


    async def chat_message(self, event):
        message_content = event['content']
        message_id = event['message_id']
        sender_id = event['sender_id']

        # 클라이언트로 메시지 전송
        await self.send(text_data=json.dumps({
            'content': message_content,
            'sender_id': sender_id,
            'message_id': message_id,
            'read_by': []  # 초기에는 아무도 읽지 않았음을 나타내는 빈 리스트
        }))

    async def chat_file(self, event):
        file_url = event['file_url']
        file_id = event['file_id']
        sender_id = event['sender_id']

        # 클라이언트로 메시지 전송
        await self.send(text_data=json.dumps({
            'file_url': file_url,
            'sender_id': sender_id,
            'file_id': file_id,
            'read_by': []  # 초기에는 아무도 읽지 않았음을 나타내는 빈 리스트
        }))


async def message_read(self, event):
    message_id = event['message_id']
    user_id = event['user_id']

    # 해당 메시지의 read_by 필드에 유저의 ID 추가
    read_by_list = read_status.get(message_id, [])
    read_by_list.append(user_id)
    read_status[message_id] = read_by_list

    # 메시지를 읽은 사람의 정보를 포함하여 클라이언트로 전송
    await self.send(text_data=json.dumps({
        'message_id': message_id,
        'user_id': user_id,
        'read_by': read_by_list
    }))

async def file_read(self, event):
    file_id = event['file_id']
    user_id = event['user_id']

    # 해당 메시지의 read_by 필드에 유저의 ID 추가
    read_by_list = read_status.get(file_id, [])
    read_by_list.append(user_id)
    read_status[file_id] = read_by_list

    # 메시지를 읽은 사람의 정보를 포함하여 클라이언트로 전송
    await self.send(text_data=json.dumps({
        'file_id': file_id,
        'user_id': user_id,
        'read_by': read_by_list
    }))