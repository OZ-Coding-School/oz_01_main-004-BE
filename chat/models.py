# chat/models.py

from django.db import models
from django.db.models import UniqueConstraint

from common.models import Common
from users.models import CustomUser


class ChatRoom(Common):
    name = models.CharField(max_length=100, null=True, blank=True)
    participant = models.ManyToManyField(CustomUser, related_name="chat_rooms")

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ", ".join([str(user) for user in self.participant.all()])


class ChatMessage(Common):
    room = models.ForeignKey(ChatRoom, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    content = models.TextField()

    def __str__(self):
        sender_name = self.sender.nickname if self.sender else "Unknown"
        return f"{sender_name}: {self.content}"


class ChatFile(Common):
    room = models.ForeignKey(ChatRoom, related_name="files", on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    file_name = models.CharField(max_length=225, blank=True, null=True)
    file_url = models.FileField(upload_to="chat_files/")

    def __str__(self):
        sender_name = self.sender.nickname if self.sender else "Unknown"
        return f"{sender_name}: {self.file_url}, {self.file_name}"


class LastRead(Common):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True)
    last_read_message = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL, null=True, blank=True)
    last_read_file = models.ForeignKey(ChatFile, on_delete=models.SET_NULL, null=True, blank=True)


from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import ChatRoom, LastRead


@receiver(m2m_changed, sender=ChatRoom.participant.through)
def create_last_read_for_participants(sender, instance, action, **kwargs):
    if action == "post_add":
        for participant_id in kwargs["pk_set"]:
            LastRead.objects.get_or_create(user_id=participant_id, chat_room=instance)
