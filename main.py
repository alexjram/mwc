import json
import os
from typing import Callable
from dotenv import load_dotenv
from utils.amqp_message_handler import AMQPMessageHandler
from utils.gps_processor import GPSProcessor
from utils import amqp_client, amqp_worker, data_processor
from utils.file_reader import FileParser


load_dotenv()

class Main:
    
    enabled: bool
    data: list[dict]
    active_data: list[dict]
    amqp_manager: amqp_client.AMQPClient
    worker: amqp_worker.AMQPWorker
    gps_processor: GPSProcessor
    message_handler: AMQPMessageHandler
    
    def __init__(self) -> None:
        self.data = []
        self.active_data = []
    
    def start(self) -> None:
        
        self.init_gps_processing()
        self.enabled = True
        file_parser = FileParser(os.getenv('DATA_FILE') or '')
        self.data = file_parser.load_json()
        
        api_data = data_processor.DataProcessor.normalize(self.gps_processor.http_worker.client.get_gps_list())
        for d in api_data:
            added = False
            for i in range(len(self.data)):
                if d['code'] == self.data[i]['code']:
                    added = True
                    if len(self.data[i]['coordinates']) == 0:
                        self.data[i]['coordinates'] = d['coordinates']
            if not added:
                self.data.append(d)
        
        print(self.data[0].keys())
        
        def callback(ch, method, properties, body):
            data = json.loads(body)
            self.data, self.active_data = self.message_handler.handle(self.data, self.active_data, properties.headers['type'], data)
            self.gps_processor.set_active_data(self.active_data)
        
        self.init_worker(callback)
        
        print('running this thing')
        
        self.gps_processor.process()
            
    def stop(self) -> None:
        self.gps_processor.disable()
        self.worker.stop()
        

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
        
    def init_gps_processing(self) -> None:
        self.gps_processor = GPSProcessor(
            self.active_data, 
            os.getenv('BACKEND_URL') or 'localhost', 
            os.getenv('SECONDS_TO_RETRY') or '30', 
            os.getenv('API_TOKEN') or None, 
            os.getenv('XRF_USERNAME') or '', 
            os.getenv('XRF_PASSWORD') or ''
        )
        def active_gps_callback(data: dict):
            if data['input'] is not None and data['output'] is not None and data['streamer'] is None:
                print('print creating streamer')
                
                
        def removed_gps_callback(data: dict):
            if data['streamer'] is not None:
                data['streamer'].stop()
                data['streamer'] = None
        self.message_handler = AMQPMessageHandler(active_gps_callback, removed_gps_callback)
    
    
if __name__ == '__main__':
    main = Main()
    try:
        main.start()
    except KeyboardInterrupt:
        main.stop()
        pass