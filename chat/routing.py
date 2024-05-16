from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"api/v1/chat/ws/chatrooms/(?P<room_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
