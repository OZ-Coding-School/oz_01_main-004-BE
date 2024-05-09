from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import ChatMessage, ChatFile

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 웹소켓 연결 시 실행되는 메서드
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'chat_%s' % self.room_id

        # 채팅방 그룹에 참여
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 웹소켓 연결 종료 시 실행되는 메서드
        # 채팅방 그룹에서 탈퇴
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def fetch_messages(self, event):
        # 새로운 메시지를 가져오는 이벤트 핸들러
        messages = await self.get_messages()
        files = await self.get_files()
        await self.send(text_data=json.dumps({
            'messages': messages,
            'files': files
        }))

    async def get_messages(self):
        # 데이터베이스에서 새로운 메시지를 가져오는 메서드
        room_id = self.scope['url_route']['kwargs']['room_id']
        messages = ChatMessage.objects.filter(room_id=room_id).values('id', 'message', 'sender_id', 'created_at')
        return list(messages)

    async def get_files(self):
        # 데이터베이스에서 파일 메시지를 가져오는 메서드
        room_id = self.scope['url_route']['kwargs']['room_id']
        files = ChatFile.objects.filter(room_id=room_id).values('id', 'file_url', 'sender_id', 'created_at')
        return list(files)

    async def receive(self, text_data):
        # 클라이언트로부터 메시지를 받는 메서드
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 메시지를 데이터베이스에 저장
        ChatMessage.objects.create(
            message=message,
            sender=self.scope['user'],
            room_id=self.room_id
        )

        # 새로운 메시지를 가져오는 이벤트를 트리거
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'fetch_messages'
            }
        )