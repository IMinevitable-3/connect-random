import json
from channels.generic.websocket import JsonWebsocketConsumer, AsyncWebsocketConsumer
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache
from server.settings import CACHE_TTL

logger = logging.getLogger(__name__)


class OnlineConsumer(JsonWebsocketConsumer):

    def connect(self):
        session = self.scope.get("session")
        if session:
            session_key = session.session_key
            if session_key:
                super().connect()
                cache.set(session_key, 0, timeout=CACHE_TTL)
                async_to_sync(self.channel_layer.group_add)(
                    session_key, self.channel_name
                )
                logger.info(f"I am online: {session_key}")

            else:
                logger.warning("Session key is not available.")
                self.close()
        else:
            logger.warning("Session object is not available in the scope.")
            self.close()

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        logger.info(f"Received WebSocket message: {text_data}")
        self.send(text_data="Hello world!")

    def group_name_update(self, event):
        message = event["message"]
        self.send_json(message)

    def disconnect(self, code):
        session_key = self.scope.get("session").session_key
        cache.delete(session_key)
        async_to_sync(self.channel_layer.group_discard)(session_key, self.channel_name)
        logger.info(f"I am offline: {session_key}")

        self.close(code)


class GroupConsumer(AsyncWebsocketConsumer):
    def connect(self):
        return super().connect()

    def disconnect(self, code):
        return super().disconnect(code)


class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        logger.info(f" echo echo..  ")

        self.channel_layer.group_add("ks", self.channel_name)

    async def disconnect(self, close_code):
        self.channel_layer.group_discard("ks", self.channel_name)
        logger.info(f"ti ti tiiin")

        self.close()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.send(text_data=json.dumps({"message": message}))
