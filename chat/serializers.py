from operator import attrgetter

from rest_framework import serializers

from .models import ChatFile, ChatMessage, ChatRoom
from users.models import CustomUser


class UserChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','nickname','email','profile_image']


class MessageSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    def get_messages(self, obj):
        messages = list(obj.chatmessage_set.all()) + list(obj.chatfile_set.all())
        sorted_messages = sorted(messages, key=lambda x: x.created_at, reverse=True)
        serialized_data = []
        for message in sorted_messages:
            if isinstance(message, ChatMessage):
                serialized_data.append(ChatMessageSerializer(message).data)
            elif isinstance(message, ChatFile):
                serialized_data.append(ChatFileSerializer(message).data)
        return serialized_data


class ChatFileSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=ChatRoom.objects.all())
    sender_data = UserChatSerializer(source='sender', read_only=True)

    class Meta:
        model = ChatFile
        fields = "__all__"


class ChatMessageSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=ChatRoom.objects.all())
    sender_data = UserChatSerializer(source='sender', read_only=True)

    class Meta:
        model = ChatMessage
        fields = "__all__"


class ChatRoomSerializer(serializers.ModelSerializer):
    participant_data = UserChatSerializer(source='participant', many=True, read_only=True)
    participant = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=True
    )

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'created_at', 'participant_data', 'participant']
        extra_kwargs = {
            'participant': {'write_only': True}
        }

    def create(self, validated_data):
        participants = validated_data.pop('participant', [])
        chat_room = ChatRoom.objects.create(**validated_data)
        chat_room.participant.set(participants)
        return chat_room


class ChatRoomDetailSerializer(serializers.ModelSerializer):
    participant_data = UserChatSerializer(source='participant', many=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'created_at', 'participant_data', 'messages']

    def get_messages(self, obj):
        messages = list(obj.chatmessage_set.all()) + list(obj.chatfile_set.all())
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


