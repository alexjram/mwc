import json
import sys
from time import sleep
import os
from typing import Callable
from dotenv import load_dotenv
from utils.http_worker import HttpWorker
from utils import amqp_client, amqp_worker
from utils.backend_client import BackendClient
from utils.file_reader import FileParser
from utils.streamer import Streamer


load_dotenv()

class Main:
    
    enabled: bool
    secondToRetry: int
    client: BackendClient
    data: list[dict]
    active_data: list[dict]
    amqp_manager: amqp_client.AMQPClient
    worker: amqp_worker.AMQPWorker
    http_worker: HttpWorker
    
    def start(self) -> None:
        
        self.init_client()
        
        self.enabled = True
        self.secondToRetry = 30
        
        file_parser = FileParser(os.getenv('DATA_FILE') or '')
        file_parser.load_json()
        self.client.check_if_server_is_up()
        
        def active_gps_callback(data: dict):
            if data['input'] is not None and data['output'] is not None and data['streamer'] is None:
                print('print creating streamer')
                
                
        def removed_gps_callback(data: dict):
            if data['streamer'] is not None:
                data['streamer'].stop()
                data['streamer'] = None
        
        def callback(ch, method, properties, body):
            data = json.loads(body)
            file_parser.filter_active(data['added'], data['removed'], active_gps_callback, removed_gps_callback)       
            self.active_data = file_parser.active_data
        
        self.init_worker(callback)
        
        print('running this thing')
        
        i = 0
        while self.enabled:
            if i == sys.maxsize - 1000:
                i = 0
            if len(file_parser.active_data) == 0:
                sleep(1)
                i += 1
                continue
            data_to_send = self.get_data(file_parser.active_data, i)
            if len(data_to_send) > 0:
                print(f"time: {i} seconds")
                self.http_worker.send_message('save_logs_batch', data_to_send)
            sleep(1)
            i += 1
            
    def stop(self) -> None:
        self.worker.stop()
        self.enabled = False
        
    def init_client(self) -> None:

        self.client = BackendClient(
            os.getenv('BACKEND_URL') or '',
            os.getenv('SECONDS_TO_RETRY') or '30',
            os.getenv('API_TOKEN') or None
        )
        self.client.set_xrf_auth(
            os.getenv('XRF_USERNAME') or '',
            os.getenv('XRF_PASSWORD') or ''
        )
        
        self.http_worker = HttpWorker(self.client)
        self.http_worker.start()
    def init_worker(self, callback: Callable) -> None:
        self.worker = amqp_worker.AMQPWorker(
            os.getenv('AMQP_URL') or 'localhost',
            int(os.getenv('AMQP_PORT') or "5672"),
            os.getenv('AMQP_USERNAME') or 'guest',
            os.getenv('AMQP_PASSWORD') or 'guest',
            os.getenv('AMQP_VHOST') or '/',
            os.getenv('AMQP_CHANNEL') or 'default',
            callback
        )
        self.worker.start()
    
    def get_data(self, active_data: list[dict], index: int) -> list[dict]:
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
                        self.client.send_alert_async(location['content'], {"people_present": True,}, location['image'])
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
if __name__ == '__main__':
    main = Main()
    try:
        main.start()
    except KeyboardInterrupt:
        main.stop()
        pass