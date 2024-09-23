import json
import sys
from time import sleep
import os
from dotenv import load_dotenv
from utils import amqp_client, amqp_worker
from utils.backend_client import BackendClient
from utils.file_reader import FileParser


load_dotenv()

class Main:
    
    enabled: bool
    secondToRetry: int
    client: BackendClient
    data: list[dict]
    active_data: list[dict]
    amqp_manager: amqp_client.AMQPClient
    worker: amqp_worker.AMQPWorker
    
    def start(self) -> None:
        
        self.init_client()
        
        self.enabled = True
        self.secondToRetry = 30
        
        file_parser = FileParser(os.getenv('DATA_FILE') or '')
        file_parser.load_json()
        self.client.check_if_server_is_up()
        
        def callback(ch, method, properties, body):
            data = json.loads(body)
            print(data)
            file_parser.filter_active(data['added'], data['removed'])       
            self.active_data = file_parser.active_data
            print(f"Active data: {file_parser.active_data}")
        
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
        
        print('running this thing')
        
        
        i = 0
        while self.enabled:
            data_to_send = []
            if i == sys.maxsize - 1000:
                i = 0
            if len(file_parser.active_data) == 0:
                sleep(1)
                i += 1
                continue
            for obj in file_parser.active_data:
                for location in obj.get('coordinates', []):
                    if (i % obj['total_time']) == location['seconds']:
                        if obj.get('image', None) is not None:
                            self.client.send_alert_async(obj['content_id'], {"people_present": True,}, obj['code'])
                        data_to_send.append({
                            "code": obj["code"],
                            "latitude": location["latitude"],
                            "longitude": location["longitude"],
                            "altitude": location["altitude"]
                        })
            if len(data_to_send) > 0:
                self.client.save_logs_batch(data_to_send)
                print(data_to_send)
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
    
if __name__ == '__main__':
    main = Main()
    try:
        main.start()
    except KeyboardInterrupt:
        main.stop()
        pass