import os
import json

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.sessions import SessionMiddlewareStack
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
default_asgi_application = get_asgi_application()
django_asgi_app = get_asgi_application()

from django.urls import path
from rest_api import consumers

application = ProtocolTypeRouter(
    {
        "http": default_asgi_application,
        "websocket": SessionMiddlewareStack(
            URLRouter(
                [
                    path("ws/echo/", consumers.EchoConsumer.as_asgi()),
                    path(
                        "ws/chat/online/",
                        consumers.OnlineConsumer.as_asgi(),
                    ),
                    path("ws/chat/<str:group_id>/", consumers.ChatConsumer.as_asgi()),
                ]
            ),
        ),
    }
)
