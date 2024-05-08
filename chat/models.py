# chat/models.py

from django.db import models
from django.contrib.auth.models import User


class ChatRoom(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    participant = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ', '.join([str(user) for user in self.participant.all()])


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender_name = self.sender.username if self.sender else "Unknown"
        return f"{sender_name}: {self.content}"


class ChatMessageFile(models.Model):
    filemessage = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    file = models.FileField(upload_to='chat_files/')
    created_at = models.DateTimeField(auto_now_add=True)