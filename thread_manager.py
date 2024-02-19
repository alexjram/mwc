

from threading import Event, Thread
from time import sleep

from backend_client import BackendClient
from streamer import Streamer


class ThreadManager:
    event: Event
    thread: Thread
    client: BackendClient
    code: str
    streamer: Streamer|None
    
    def __init__(self, client: BackendClient, code: str, data: dict) -> None:
        self.event = Event()
        self.client  = client
        self.code = code
        self.streamer = None
        self.start(data)
        
    def start(self, data: dict):
        print('thread started')
        if data['input'] is not None and data['output'] is not None:
            print('print creating streamer')
            self.streamer = Streamer(data['input'], data['output'])
            self.streamer.start()

        def callback(event: Event):
            while not event.is_set():
                self.save_logs(data)

        self.thread = Thread(target=callback, args=(self.event,))
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
            