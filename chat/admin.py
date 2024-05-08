from django.contrib import admin
from .models import ChatRoom, ChatMessage, ChatMessageFile


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['room', 'sender', 'content', 'created_at']
    list_filter = ['room', 'sender']


@admin.register(ChatMessageFile)
class ChatMessageFileAdmin(admin.ModelAdmin):
    pass