import sys
from time import sleep
from typing import Union
from utils.backend_client import BackendClient
from utils.http_worker import HttpWorker
from utils.streamer import Streamer


class GPSProcessor:
    http_worker: HttpWorker
    enabled: bool
    active_data: list[dict]
    all_data: list[dict]
    
    def __init__(self, active_data: list[dict], url: str, secons_to_retry: str, api_token: Union[str, None], username: str, password: str) -> None:
        client = BackendClient(url, secons_to_retry, api_token)
        client.set_xrf_auth(username, password)
        client.check_if_server_is_up()
        self.http_worker = HttpWorker(client)
        self.http_worker.start()
        self.enabled = True
        self.active_data = active_data
        
    def set_active_data(self, active_data: list[dict]):
        self.active_data = active_data
    def set_all_data(self, all_data: list[dict]):
        self.all_data = all_data
        
    def disable(self):
        self.enabled = False
    def process(self):

        i = 0
        while self.enabled:
            if 0 == sys.maxsize - 1000:
                i = 0
            if len(self.active_data) == 0:
                if i % 3600 == 0:
                    self.__send_initial_inactive()
                sleep(1)
                i += 1
                continue
            data_to_send = self.__process_item(self.active_data, i)
            if len(data_to_send) > 0:
                print(data_to_send)
                self.http_worker.send_message('gps_data', data_to_send)
            sleep(1)
            i += 1

    def __process_item(self, active_data, index: int):
        data_to_send = []
        external_codes = []
        for obj in active_data:
            if obj['endpoint'] is not None and obj['refresh'] is not None and index % obj['refresh'] == 0:
                print('is external request')
                external_codes.append(obj['code'])
                self.http_worker.send_message('external_request', {"code": obj['code'], "endpoint": obj['endpoint'], "method": 'GET'})
                continue
            
            if obj['streamer'] is None and obj['input'] is not None and obj['output'] is not None and (index % obj['total_time']) == 0:
                streamer = Streamer(obj['input'], obj['output'])
                obj['streamer'] = streamer
                
            for location in obj.get('coordinates', []):
                if (index % obj['total_time']) == location['seconds']:
                    if location['image'] is not None:
                        print('is image')
                        self.http_worker.send_message('send_alert', {
                            "content_id": location['content'],
                            "events": {"people_present": True},
                            "image": location['image']
                        })
                    data_to_send.append({
                        "code": obj["code"],
                        "latitude": location["latitude"],
                        "longitude": location["longitude"],
                        "altitude": location["altitude"]
                    })
        return data_to_send
    
    def __send_initial_inactive(self):
        send_data = []
        for da in self.all_data:
            if len(da['coordinates']) == 0:
                continue
            send_data.append({
                'code': da['code'],
                'latitude': da['coordinates'][0]['latitude'],
                'longitude': da['coordinates'][0]['longitude'],
                'altitude': da['coordinates'][0]['altitude'],
            })
        self.http_worker.send_message('gps_data', send_data)