# chat/models.py

from django.db import models
from django.contrib.auth.models import User


class ChatRoom(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User, related_name='chat_rooms')

    def __str__(self):
        return self.name

    @staticmethod
    def create_chatroom(user1, user2):
        # 자신의 이름을 필터링하여 채팅방 이름 생성
        if user1.username == user2.username:
            chatroom_name = f"Chat with {user2.username}"
        else:
            chatroom_name = f"Chat between {user1.username} and {user2.username}"

        # 채팅방 생성
        chatroom = ChatRoom.objects.create(name=chatroom_name)
        chatroom.users.add(user1, user2)

        return chatroom


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content}"
