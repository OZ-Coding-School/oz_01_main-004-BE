# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'chat_room'
        self.room_group_name = 'chat_%s' % self.room_name

        # 해당 채팅 그룹에 연결합니다.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 해당 채팅 그룹에서 연결을 해제합니다.
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 메시지를 수신하여 해당 채팅 그룹에 브로드캐스트합니다.
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        # 채팅 그룹에 메시지를 브로드캐스트합니다.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': username,
                'message': message
            }
        )

    # 채팅 그룹으로부터 메시지를 수신하여 클라이언트에게 전송합니다.
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # WebSocket으로 메시지를 보냅니다.
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
