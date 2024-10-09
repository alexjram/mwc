import threading
from typing import Callable

import pika
import pika.channel


class AMQPWorker:
    callback: Callable
    host: str
    port: int
    username: str
    password: str
    vhost: str
    connection: pika.SelectConnection
    queue: str
    thread: threading.Thread
    event: threading.Event
    channel: pika.channel.Channel
    
    def __init__(self, host: str, port:int, username: str, password: str, vhost: str, queue: str, callback: Callable) -> None:
        self.callback = callback
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.vhost = vhost
        self.queue = queue

    def start(self) -> None:
        self.connection = pika.SelectConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=pika.PlainCredentials(self.username, self.password),
                virtual_host=self.vhost
            ),
            on_open_callback=self.on_connection_opened
        )
        
        def init_thread():
            self.connection.ioloop.start()
        
        try:
            self.thread = threading.Thread(target=init_thread)
            self.thread.start()
        except KeyboardInterrupt:
            self.connection.close()
        
    def on_connection_opened(self, connection:pika.SelectConnection):
        self.channel = connection.channel(on_open_callback=self.on_channel_opened)
    
    def on_channel_opened(self, channel: pika.channel.Channel):
        def my_callback(channel, method, properties, body):
            self.callback(channel, method, properties, body)
        self.channel.basic_consume(queue=self.queue, on_message_callback=my_callback, auto_ack=True)
    

    def stop(self) -> None:
        self.connection.ioloop.stop()
        self.channel.close()
        self.connection.close()
        self.thread.join()
        