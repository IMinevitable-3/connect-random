from celery import Celery
from celery import shared_task

app = Celery("server")


@app.task(serializer="json", name="pair_messages")
def process_paired_queue_message(m1, m2):
    print("Received message from paired_queue:", m1, m2)
