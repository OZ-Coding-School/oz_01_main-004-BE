# chat/models.py

from django.db import models

from users.models import CustomUser


class ChatRoom(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    participant = models.ManyToManyField(CustomUser, related_name="chat_rooms")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ", ".join([str(user) for user in self.participant.all()])


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender_name = self.sender.nickname if self.sender else "Unknown"
        return f"{sender_name}: {self.content}"


class ChatFile(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to="chat/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender_name = self.sender.nickname if self.sender else "Unknown"
        return f"{sender_name}: {self.file}"
