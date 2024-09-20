from typing import Callable
import pika


class AMQPClient:

    def __init__(self, host: str, port: int, username: str, password: str, vhost: str, channel, callback: Callable):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=pika.PlainCredentials(username, password),
                virtual_host=vhost
            )
        )
        self.channel = self.connection.channel()
        
        #self.channel.queue_declare(queue=channel, durable=True)
        self.channel.basic_consume(queue=channel, on_message_callback=callback, auto_ack=True)
