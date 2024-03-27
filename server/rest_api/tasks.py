from celery import Celery
from django.core.cache import cache
from server.settings import CACHE_TTL
from .rabbit import AMQPManager
from environ import (
    CLIENT_QUEUE_HOST,
    CLIENT_QUEUE_PASSWORD,
    CLIENT_QUEUE_PORT,
    CLIENT_QUEUE_QUEUE_NAME,
    CLIENT_QUEUE_USER,
)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

app = Celery("server")


def check_waiting(group_name):
    return cache.get(group_name)


def send_again(queue, message):
    try:
        queue.publish_message(CLIENT_QUEUE_QUEUE_NAME, message)
    except Exception as e:
        print(e)


@app.task(serializer="json", name="pair_messages")
def process_paired_queue_message(m1, m2):
    client_1 = m1["id"]
    client_2 = m2["id"]
    status_of_c1 = check_waiting(client_1)
    status_of_c2 = check_waiting(client_2)
    if status_of_c1 >= 3:
        cache.delete(client_1)
        return
    if status_of_c2 >= 3:
        cache.delete(client_2)
        return
    cache.set(client_1, status_of_c1 + 1, timeout=CACHE_TTL)
    cache.set(client_2, status_of_c2 + 1, timeout=CACHE_TTL)

    amqp_manager = AMQPManager(
        f"amqp://{CLIENT_QUEUE_USER}:{CLIENT_QUEUE_PASSWORD}@{CLIENT_QUEUE_HOST}:{CLIENT_QUEUE_PORT}/"
    )
    if status_of_c1 is None:
        send_again(amqp_manager, m2)
        return 0
    if status_of_c2 is None:
        send_again(amqp_manager, m1)
        return 0

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        client_1,
        {
            "type": "group_name_update",
            "message": {
                "room_name": f"room_{client_1}_{client_2}",
                "command": "connect now",
            },
        },
    )
    async_to_sync(channel_layer.group_send)(
        client_2,
        {
            "type": "group_name_update",
            "message": {
                "room_name": f"room_{client_1}_{client_2}",
                "command": "connect now",
            },
        },
    )
