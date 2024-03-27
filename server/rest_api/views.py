from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status
import uuid
from environ import CLIENT_QUEUE_QUEUE_NAME
from environ import (
    CLIENT_QUEUE_HOST,
    CLIENT_QUEUE_PASSWORD,
    CLIENT_QUEUE_PORT,
    CLIENT_QUEUE_USER,
)
from .rabbit import AMQPManager
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
                # with Connection(
                #     f"amqp://{CLIENT_QUEUE_USER}:{CLIENT_QUEUE_PASSWORD}@{CLIENT_QUEUE_HOST}:{CLIENT_QUEUE_PORT}/"
                # ) as connection:
                #     exchange = Exchange("")
                #     producer = Producer(connection, exchange)
                #     message_body = json.dumps({"id": ss})
                #     producer.publish(
                #         message_body,
                #         routing_key=CLIENT_QUEUE_QUEUE_NAME,
                #         content_type="application/json",
                #         content_encoding="utf-8",
                #     )
                amqp_manager = AMQPManager(
                    f"amqp://{CLIENT_QUEUE_USER}:{CLIENT_QUEUE_PASSWORD}@{CLIENT_QUEUE_HOST}:{CLIENT_QUEUE_PORT}/"
                )

                message = {"id": ss}
                routing_key = CLIENT_QUEUE_QUEUE_NAME
                amqp_manager.publish_message(routing_key, message)

                amqp_manager.close_connection()
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "no token"}, status=status.HTTP_404_NOT_FOUND)

        return Response({}, status=status.HTTP_201_CREATED)


# sessionid=nad9msuk5nknacj7l093xl86p2yrvz1i; Path=/; HttpOnly; Expires=Tue, 26 Mar 2024 23:40:35 GMT;
