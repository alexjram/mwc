import json
from time import sleep
import os
from typing import Union
from dotenv import load_dotenv

from utils.backend_client import BackendClient


load_dotenv()

class Main:
    
    enabled: bool
    secondToRetry: int
    client: BackendClient
    data: list[dict[str, Union[str, list[dict]]]]
    
    def start(self) -> None:
        
        self.client = BackendClient(
            os.getenv('BACKEND_URL') or '',
            os.getenv('SECONDS_TO_RETRY') or '30',
            os.getenv('API_TOKEN') or None
        )

        self.enabled = True
        self.secondToRetry = 30
        
        file = open(os.getenv('DATA_FILE') or '', 'r')
        data = json.load(file)
        file.close()
        
        self.client.check_if_server_is_up()
        
        
        
        while self.enabled:
            print('2 seconds passed')
            sleep(2)
            
    def normalize_data(self, data: list):
        
        for datum in data:
            pass