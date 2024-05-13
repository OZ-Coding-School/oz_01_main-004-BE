from operator import attrgetter

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import ChatFile, ChatMessage, ChatRoom


class ChatFileSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=ChatRoom.objects.all())

    class Meta:
        model = ChatFile
        fields = "__all__"


class ChatMessageSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=ChatRoom.objects.all())

    class Meta:
        model = ChatMessage
        fields = "__all__"


class ChatRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatRoom
        fields = "__all__"


class ChatRoomDetailSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = "__all__"

    def get_messages(self, obj):
        messages = list(obj.chatmessage_set.all()) + list(obj.chatmessagefile_set.all())
        sorted_messages = sorted(messages, key=lambda x: x.created_at, reverse=True)
        serialized_data = []
        for message in sorted_messages:
            if isinstance(message, ChatMessage):
                serialized_data.append(ChatMessageSerializer(message).data)
            elif isinstance(message, ChatFile):
                serialized_data.append(ChatFileSerializer(message).data)
        return serialized_data
        # reverse=True 내림차순,reverse=False/생략 오름차순

    # def get_room_name(self, instance):
    #     return self.context.get('room_name', None)


class ChatRoomNameUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatRoom
        fields = ("name",)
