from kombu import Connection, Exchange, Producer
import json


class AMQPManager:
    def __init__(self, url):
        self.connection = Connection(url)
        self.channel = self.connection.channel()
        self.exchange = Exchange("", channel=self.channel, durable=False)

    def publish_message(self, routing_key, message):
        producer = Producer(
            self.channel, exchange=self.exchange, routing_key=routing_key
        )
        producer.publish(
            json.dumps(message),
            content_type="application/json",
            content_encoding="utf-8",
        )

    def close_connection(self):
        self.connection.close()
