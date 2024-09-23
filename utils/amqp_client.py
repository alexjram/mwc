import threading
from typing import Callable, Union
import pika


class AMQPClient:
    
    callback: Callable
    connection: Union[pika.BlockingConnection, pika.SelectConnection, None]
    queue: str
    enabled: bool
    thread: threading.Thread

    def sync_init(self, host: str, port: int, username: str, password: str, vhost: str, channel, callback: Callable):
        
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=pika.PlainCredentials(username, password),
                virtual_host=vhost,
            )
        )
        self.channel = self.connection.channel()
        
        def my_callback(channel, method, properties, body):

            callback(channel, method, properties, body)
        
        #self.channel.queue_declare(queue=channel, durable=True)
        self.channel.basic_consume(queue=channel, on_message_callback=my_callback, auto_ack=True)
        
        self.channel.start_consuming()


    def async_init(self, host: str, port: int, username: str, password: str, vhost: str, channel, callback: Callable):
        self.queue = channel
        self.connection = pika.SelectConnection(
            parameters=pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=pika.PlainCredentials(username, password),
                virtual_host=vhost,
            ),
            on_open_callback=self.on_connection_opened,
        )
        self.enabled = True
        def run_io_loop(conn):
            conn.ioloop.start()
            self.channel.start_consuming()
        if self.connection:
            
            self.thread = threading.Thread(target=run_io_loop, args=(self.connection,))
            self.thread.start()
            
            
    def on_connection_opened(self, connection):
        if self.connection is pika.SelectConnection:
            self.connection.channel(on_open_callback=self.channel_callback)
        
        
    def channel_callback(self, ch):
        ch.queue_declare(queue=self.queue, durable=True)
        ch.basic_consume(queue=self.queue, on_message_callback=self.callback, auto_ack=True)
        
    def stop(self):
        self.enabled = False
        self.thread.join()
        if self.connection is not None:
            self.connection.close()