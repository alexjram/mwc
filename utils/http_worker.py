from operator import is_
from queue import Queue 
from threading import Event, Thread
from typing import Union

from utils.backend_client import BackendClient


class HttpWorker:
    queue: Queue
    thread: Thread
    client: BackendClient
    event: Event
    
    def __init__(self, client: BackendClient) -> None:
        self.client = client
       
    def start(self):
        self.event = Event()
        self.queue = Queue()
        def worker(event: Event) -> None:
            is_set = False
            while not event.is_set() and not is_set:
                item = self.queue.get()
                print('processing item')
                if item is None:
                    is_set = True
                try:
                    self.process(item)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(e)
                self.queue.task_done()
            while not self.queue.empty():
                self.queue.get()
                self.queue.task_done
            #self.stop()
        
        self.thread = Thread(target=worker, daemon=True, args=(self.event,))
        self.thread.start()
        
    def stop(self) -> None:
        self.event.set()
        self.queue.put(None)
        print('stopping worker')
        print('stoping queue')
        self.queue.join()
        print('stopping thread')
        self.thread.join()
        print('stopped worker')
    
    def process(self, item: dict) -> None:
        action = item['action']
        payload = item['payload']
        
        if action == 'save_logs_batch' or action == 'gps_data':
            self.client.save_logs_batch(payload)
        if action == 'send_location':
            self.client.send_location(payload['latitude'], payload['longitude'], payload['code'], payload['altitude'], payload['rel_altitude'])
        if action == 'send_alert':
            self.client.send_alert_async(payload['content_id'], payload['events'], payload['image'])
        if action.startswith('external_request'):
            self.client.external_request_async(payload['endpoint'], payload['method'], payload['code'])

    def send_message(self, action: str, payload: Union[dict, list]) -> None:
        if not self.event.is_set():
            self.queue.put({
                'action': action,
                'payload': payload
            })