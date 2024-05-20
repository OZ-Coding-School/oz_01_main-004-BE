from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"chatrooms/(?P<room_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
