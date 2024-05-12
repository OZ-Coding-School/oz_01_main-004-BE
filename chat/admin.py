from django.contrib import admin

from .models import ChatFile, ChatMessage, ChatRoom


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["room", "sender", "content", "created_at"]
    list_filter = ["room", "sender"]


@admin.register(ChatFile)
class ChatFileAdmin(admin.ModelAdmin):
    pass
