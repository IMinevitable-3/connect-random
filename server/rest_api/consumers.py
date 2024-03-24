import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer, AsyncWebsocketConsumer

import logging

logger = logging.getLogger(__name__)


class TaskProgressConsumer(JsonWebsocketConsumer):
    def celery_task_update(self, event):
        message = event["message"]
        self.send_json(message)

    def connect(self):
        super().connect()
        taskID = self.scope.get("url_route").get("kwargs").get("taskID")
        logger.info(f"Connecting to WebSocket for taskID: {taskID}")
        async_to_sync(self.channel_layer.group_add)(taskID, self.channel_name)

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        logger.info(f"Received WebSocket message: {text_data}")
        self.send(text_data="Hello world!")

    def disconnect(self, close_code):
        self.close()


class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.send(text_data=json.dumps({"message": message}))
