import json
import sys
from time import sleep
import os
from dotenv import load_dotenv
from utils import amqp_client
from utils.backend_client import BackendClient
from utils.data_processor import DataProcessor


load_dotenv()

class Main:
    
    enabled: bool
    secondToRetry: int
    client: BackendClient
    data: list[dict]
    active_data: list[dict]
    amqp_manager: amqp_client.AMQPClient
    
    def start(self) -> None:
        
        self.client = BackendClient(
            os.getenv('BACKEND_URL') or '',
            os.getenv('SECONDS_TO_RETRY') or '30',
            os.getenv('API_TOKEN') or None
        )
        self.client.set_xrf_auth(
            os.getenv('XRF_USERNAME') or '',
            os.getenv('XRF_PASSWORD') or ''
        )
        

        self.enabled = True
        self.secondToRetry = 30
        
        file = open(os.getenv('DATA_FILE') or '', 'r')
        data = json.load(file)
        file.close()
        
        self.client.check_if_server_is_up()
        
        self.data = DataProcessor.normalize(data)
        
        self.active_data = []
        
        def callback(ch, method, properties, body):
            data = json.loads(body)
            print(data)
        
        self.amqp_manager = amqp_client.AMQPClient(
            os.getenv('AMQP_URL') or 'localhost',
            int(os.getenv('AMQP_PORT') or "5672"),
            os.getenv('AMQP_USERNAME') or 'guest',
            os.getenv('AMQP_PASSWORD') or 'guest',
            os.getenv('AMQP_VHOST') or '/',
            os.getenv('AMQP_CHANNEL') or 'default',
            callback
        )
        
        #self.amqp_client.start()
        
        i = 0
        while self.enabled:
            data_to_send = []
            if i == sys.maxsize - 1000:
                i = 0
            if len(self.active_data) == 0:
                sleep(1)
                i += 1
                continue
            for obj in self.active_data:
                for location in obj.get('coordinates', []):
                    if (location['seconds'] % obj['total_time']) == i:
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
        self.enabled = False
    
if __name__ == '__main__':
    main = Main()
    try:
        main.start()
    except KeyboardInterrupt:
        main.stop()
        pass