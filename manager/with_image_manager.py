import utils.common_utils

from threading import Event, Thread
from time import sleep

from utils.backend_client import BackendClient
from manager.base_manager import BaseManager

class WithImageManager(BaseManager):

    def __init__(self, client: BackendClient, data: dict) -> None:
        super().__init__(client, data)

    def start(self, data: dict):
        self.print('Thread started')

        def callback(event: Event):
            while not event.is_set():
                self.process(data)
        
        def callback_no_send(event: Event):
            while not event.is_set():
                sleep(1)
            
        target = callback    
        if not 'code' in data:
            target = callback_no_send

        self.thread = Thread(target=target, args=(self.event,))
        self.thread.start()

    def process(self, data: dict) -> None:

        time = 0
        coordinates = data["coordinates"]
        for coor in coordinates:
            seconds = utils.common_utils.time_convert(coor["time"])
            for _ in range(seconds - time):
                if self.event.is_set():
                    return
                sleep(1)
            
            altitude = float(coor.get('altitude', data.get('altitude', 0)))
            rel_altitude = float(coor.get('rel_altitude', data.get('rel_altitude', 0)))
            utils.common_utils.loop_until_is_done(self, lambda: self.client.send_location(coor['latitude'], coor['longitude'], data['code'], altitude, rel_altitude))

            image = coor.get('image', None)
            content_id = coor.get('content', None)
            if image is not None and content_id is not None:            
                utils.common_utils.loop_until_is_done(self, lambda: self.send_alert(image, content_id))

            time = seconds

    def send_alert(self, image: str, content_id: str) -> None:
        raw_data = utils.common_utils.read_document(image)
        image = ('image.png', raw_data, 'image/png')

        events = {"people_present": True,}

        self.client.send_alert(content_id, events, image)

    def print(self, message) -> None:
        print(f"WITH_PHOTO: {message}")

    def stop(self) -> None:
        super().stop()
