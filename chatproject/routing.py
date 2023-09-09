# routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from auth_app import consumers

application = ProtocolTypeRouter(
    {
        "websocket": URLRouter(
            [
                re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
            ]
        ),
    }
)
