from rest_framework import serializers
from .models import ChatRoom, ChatMessage, ChatMessageFile
from django.contrib.auth.models import User

class ChatMessageFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatMessageFile
        fields = '__all__'


class ChatMessageSerializer(serializers.ModelSerializer):
    chatmessagefile_set = ChatMessageFileSerializer(many=True, read_only=True)  # 이 부분을 수정합니다.

    class Meta:
        model = ChatMessage
        fields = '__all__'


class ChatRoomSerializer(serializers.ModelSerializer):
    chatmessage_set = ChatMessageSerializer(many=True, read_only=True)  # 이 부분을 수정합니다.
    # room_name = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = '__all__'

    # def get_room_name(self, instance):
    #     return self.context.get('room_name', None)



class ChatRoomNameUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatRoom
        fields = ('name',)