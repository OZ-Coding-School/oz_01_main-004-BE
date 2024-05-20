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
        messages = list(obj.messages.all()) + list(obj.files.all())
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
    latest_message = serializers.SerializerMethodField()


    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'created_at', 'participant_data', 'participant', 'latest_message']
        extra_kwargs = {
            'participant': {'write_only': True}
        }

    def get_latest_message(self, obj):
        # 가장 최신의 메시지와 파일을 찾습니다.
        latest_message = obj.messages.order_by('-created_at').first()
        latest_file = obj.files.order_by('-created_at').first()

        # 최신 메시지와 파일 중에서 더 최신인 것을 선택합니다.
        latest = None
        if latest_message and latest_file:
            latest = latest_message if latest_message.created_at > latest_file.created_at else latest_file
        elif latest_message:
            latest = latest_message
        elif latest_file:
            latest = latest_file

        # 최신 메시지가 있으면 시리얼라이즈하여 반환합니다.
        if latest:
            if isinstance(latest, ChatMessage):
                return ChatMessageSerializer(latest).data
            elif isinstance(latest, ChatFile):
                return ChatFileSerializer(latest).data

        return None

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
        messages = list(obj.messages.all()) + list(obj.files.all())
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


