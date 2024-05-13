

import random
import string
from threading import Event, Thread
from time import sleep

from backend_client import BackendClient
from streamer import Streamer


class ThreadManager:
    event: Event
    thread: Thread
    client: BackendClient
    code: str|None
    streamer: Streamer|None
    
    def __init__(self, client: BackendClient, data: dict) -> None:
        self.event = Event()
        self.client  = client
        self.code = data.get('code', ''.join(random.choices(string.ascii_uppercase, k=6)))
        self.streamer = None
        self.start(data)
        
    def start(self, data: dict):
        print('thread started')
        if "input" in data and data['input'] is not None and "output" in data and data['output'] is not None:
            print('print creating streamer')
            self.streamer = Streamer(data['input'], data['output'])
            self.streamer.start()

        def callback(event: Event):
            while not event.is_set():
                self.save_logs(data)
        
        def callback_no_send(event: Event):
            while not event.is_set():
                sleep(1)
            
        target = callback    
        if not 'code' in data:
            target = callback_no_send

        self.thread = Thread(target=target, args=(self.event,))
        self.thread.start()
        
    def save_logs(self, data: dict) -> None:
        time = 0
        coordinates = data["coordinates"]
        for coor in coordinates:
            seconds = self.time_convert(coor["time"])
            for i in range(seconds - time):
                if self.event.is_set():
                    return
                sleep(1)
            time = seconds
            self.client.send_location(coor['latitude'], coor['longitude'], data['code'])
            
    def time_convert(self, time: str) -> int:
        seconds = 0
        time_parts = time.split(':')
        seconds = int(time_parts[0]) * 60 + int(time_parts[1])
        return seconds
    
    def stop(self) -> None:
        self.event.set()
        self.thread.join()
        print('Stopped thread')
        if self.streamer is not None:
            self.streamer.stop()
            