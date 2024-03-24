import json
import random
import string
import pika
import time
import os
import signal
from dotenv import load_dotenv
from kombu import Connection, Exchange, Producer

load_dotenv()

MATCH_THRESHOLD = 3

CLIENT_QUEUE_USER = os.environ.get("CLIENT_QUEUE_USER", "user")
CLIENT_QUEUE_PASSWORD = os.environ.get("CLIENT_QUEUE_PASSWORD", "password")
CLIENT_QUEUE_HOST = os.environ.get("CLIENT_QUEUE_HOST", "localhost")
CLIENT_QUEUE_PORT = os.environ.get("CLIENT_QUEUE_PORT", 5672)
CLIENT_QUEUE_QUEUE_NAME = os.environ.get("CLIENT_QUEUE_QUEUE_NAME", "waiting_queue")
CLIENT_QUEUE_RESULT = os.environ.get("CLIENT_QUEUE_RESULT", "paired_queue")


broker_url = f"amqp://{CLIENT_QUEUE_USER}:{CLIENT_QUEUE_PASSWORD}@{CLIENT_QUEUE_HOST}:{CLIENT_QUEUE_PORT}"
import uuid


def create_celery_message(task_name=None, args=None, kwargs=None, retries=0):
    """
    Create a Celery message in the required format.

    Args:
        task_name (str): Name of the Celery task.
        args (list, optional): Positional arguments for the task. Defaults to None.
        kwargs (dict, optional): Keyword arguments for the task. Defaults to None.
        retries (int, optional): Number of retries for the task. Defaults to 0.

    Returns:
        dict: Celery message in the required format.
    """
    message_id = str(uuid.uuid4())
    message_task_name = "pair_messages"
    message_args = [args["p1"], args["p2"]] if args is not None else []
    message_kwargs = kwargs if kwargs is not None else {}
    message_retries = retries

    message = {
        "id": message_id,
        "task": message_task_name,
        "args": message_args,
        "kwargs": message_kwargs,
        "retries": message_retries,
    }
    return message


def send_pairs(pair):
    try:
        with Connection(broker_url) as connection:
            exchange = Exchange("")
            producer = Producer(connection, exchange)
            mess = create_celery_message(args=pair)
            message_body = json.dumps(mess)
            producer.publish(
                message_body,
                routing_key=CLIENT_QUEUE_RESULT,
                content_type="application/json",
                content_encoding="utf-8",
            )
            print("message delivered")
    except Exception as e:
        print(e)


with Connection(broker_url) as conn:
    simple_queue = conn.SimpleQueue(CLIENT_QUEUE_QUEUE_NAME)
    queue_size = simple_queue.qsize()

    for i in range((queue_size - 2) // 2):
        l = ["p1", "p2"]
        pair = {}

        for j in range(2):

            message = simple_queue.get(block=False)
            # print(f"Message {i + 1}: {message.payload}")
            pair[l[j]] = message.payload
            message.ack()
        print(pair)

        send_pairs(pair)

    simple_queue.close()
