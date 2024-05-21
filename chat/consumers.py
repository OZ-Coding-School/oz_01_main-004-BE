import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatFile
from rest_framework import status


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 웹소켓 연결 시 실행되는 메서드
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # 채팅방 그룹에 참여
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # 웹소켓 연결 종료 시 실행되는 메서드
        # 채팅방 그룹에서 탈퇴
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def chat_message(self, event):
        # 채팅 메시지를 받아서 클라이언트로 전송하는 메서드
        await self.send(text_data=json.dumps({
            'content': event["message"]
        }))

    async def file_message(self, event):
        # 파일 메시지를 받아서 클라이언트로 전송하는 메서드
        user_id = self.scope["user"].id
        latest_file = await self.get_latest_file_data(user_id)
        if latest_file:
            file_url = latest_file.file_url
            await self.send(text_data=json.dumps({
                'file_url': file_url
            }))

    async def receive(self, text_data):
        # 클라이언트로부터 메시지를 받는 메서드
        text_data_json = json.loads(text_data)

        # 여기서 API 호출 로직을 수행하고, 상태 코드에 따라 다른 메시지를 전송
        # 예를 들어, API 호출은 여기서 직접 하지 않겠습니다. 대신에 상태 코드를 하드코딩합니다.
        status_code = 201  # 예시: 성공 상태 코드
        if status_code == status.HTTP_404_NOT_FOUND:
            # 채팅방이 없는 경우
            await self.send(text_data=json.dumps({'error': '없는 채팅방입니다.'}))
        elif status_code == status.HTTP_403_FORBIDDEN:
            # 참가자가 아닌 경우
            await self.send(text_data=json.dumps({'error': '채팅방에 참가자가 아닙니다.'}))
        elif status_code == status.HTTP_201_CREATED:
            # 메시지 전송
            await self.send(text_data=text_data_json['content'])

    @sync_to_async
    def get_latest_file_data(self, user_id):
        # 데이터베이스에서 최신 파일 데이터를 가져오는 메서드
        latest_file = ChatFile.objects.filter(sender_id=user_id).order_by('-created_at').first()
        return latest_file
