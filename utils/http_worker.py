from queue import Queue 
from threading import Thread
from typing import Union

from utils.backend_client import BackendClient


class HttpWorker:
    queue: Queue
    thread: Thread
    client: BackendClient
    
    def __init__(self, client: BackendClient) -> None:
        self.client = client
       
    def start(self):
        self.queue = Queue()
        def worker() -> None:
            while True:
                item = self.queue.get()
                print('processing item')
                try:
                    self.process(item)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(e)
                self.queue.task_done()
            self.stop()
        
        self.thread = Thread(target=worker, daemon=True)
        self.thread.start()
        
    def stop(self) -> None:
        for i in range(self.queue.qsize()):
            self.queue.get()
            self.queue.task_done()
        self.queue.join()
        self.thread.join()
    
    def process(self, item: dict) -> None:
        action = item['action']
        payload = item['payload']
        
        if action == 'save_logs_batch':
            self.client.save_logs_batch(payload)
        if action == 'send_location':
            self.client.send_location(payload['latitude'], payload['longitude'], payload['code'], payload['altitude'], payload['rel_altitude'])
        if action == 'send_alert':
            self.client.send_alert_async(payload['content_id'], payload['events'], payload['image'])
        if action.startswith('external_request'):
            self.client.external_request_async(payload['endpoint'], payload['method'], payload['code'])

    def send_message(self, action: str, payload: Union[dict, list]) -> None:
        self.queue.put({
            'action': action,
            'payload': payload
        })