# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import path
# from django.urls.conf import include
#
# from chat import routing as chat_routing
#
# application = ProtocolTypeRouter(
#     {
#         "websocket": URLRouter(chat_routing.websocket_urlpatterns),
#     }
# )

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from chat import routing as chat_routing

websocket_urlpatterns = [
    path("api/v1/chat/ws/", URLRouter(chat_routing.websocket_urlpatterns)),
]
