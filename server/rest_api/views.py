import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status
import uuid
from environ import CLIENT_QUEUE_QUEUE_NAME
import pika
from environ import (
    CLIENT_QUEUE_HOST,
    CLIENT_QUEUE_PASSWORD,
    CLIENT_QUEUE_PORT,
    CLIENT_QUEUE_USER,
)
from kombu import Connection, Exchange, Producer

import logging

logger = logging.getLogger(__name__)


class IssueToken(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        unique_token = uuid.uuid4().hex
        request.session["id"] = unique_token
        return Response(data={}, status=status.HTTP_200_OK)


class AddToQueue(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        unique_token = request.session.get("id")
        ss = request.session.session_key
        logger.info(f"sessionid: {ss}\n unique_token:{unique_token}")
        if unique_token:
            try:
                with Connection(
                    f"amqp://{CLIENT_QUEUE_USER}:{CLIENT_QUEUE_PASSWORD}@{CLIENT_QUEUE_HOST}:{CLIENT_QUEUE_PORT}/"
                ) as connection:
                    exchange = Exchange("")
                    producer = Producer(connection, exchange)
                    message_body = json.dumps({"id": ss})
                    producer.publish(
                        message_body,
                        routing_key=CLIENT_QUEUE_QUEUE_NAME,
                        content_type="application/json",
                        content_encoding="utf-8",
                    )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "no token"}, status=status.HTTP_404_NOT_FOUND)

        return Response({}, status=status.HTTP_201_CREATED)
