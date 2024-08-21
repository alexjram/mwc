import utils.common_utils

from threading import Event, Thread
from time import sleep

from utils.backend_client import BackendClient
from utils.streamer import Streamer

from manager.base_manager import BaseManager

class MainManager(BaseManager):

    streamer: Streamer|None
    
    def __init__(self, client: BackendClient, data: dict) -> None:
        self.streamer = None
        super().__init__(client, data)
        
    def start(self, data: dict):
        self.print('Thread started')
        if "input" in data and data['input'] is not None and "output" in data and data['output'] is not None:
            self.print('print creating streamer')
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
            seconds = utils.common_utils.time_convert(coor["time"])
            for i in range(seconds - time):
                if self.event.is_set():
                    return
                sleep(1)

            utils.common_utils.loop_until_is_done(self, lambda: self.client.send_location(coor['latitude'], coor['longitude'], data['code']))

            time = seconds
    
    def print(self, message) -> None:
        print(f"MAIN: {message}")
    
    def stop(self) -> None:
        super().stop()
        if self.streamer is not None:
            self.streamer.stop()
