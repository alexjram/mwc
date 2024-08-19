from threading import Event, Thread
from time import sleep

from utils.backend_client import BackendClient
from manager.base_manager import BaseManager

class WithEndpointManager(BaseManager):

    location: dict

    def __init__(self, client: BackendClient, data: dict) -> None:
        self.location = data.get('location', {})
        super().__init__(client, data)

    def start(self, data: dict):
        self.print('Thread started')

        def callback(event: Event):
            while not event.is_set():
                self.process(data)
        
        def callback_no_send(event: Event):
            while not event.is_set():
                sleep(self.location['refresh'])
            
        target = callback    
        if not 'code' in data:
            target = callback_no_send

        self.thread = Thread(target=target, args=(self.event,))
        self.thread.start()

    def process(self, data: dict) -> None:

        sent = False
        gps_endpoint = self.location['endpoint']
        while not sent:
            try:
                response = self.client.external_request(endpoint=gps_endpoint, method='GET')

                lat, long = response['latLng'].split(',')
                self.client.send_location(float(lat), float(long), data['code'])
                sent = True
            except Exception as e:
                if e.args[0] != "SERVER_OFF":
                    self.event.set()
                    return
                
                self.client.check_if_server_is_up(gps_endpoint)
                
        sleep(self.location['refresh'])

    def print(self, message) -> None:
        print(f"WITH_ENDPOINT: {message}")

    def stop(self) -> None:
        super().stop()
