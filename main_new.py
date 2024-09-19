from time import sleep
import os
from dotenv import load_dotenv

from utils.backend_client import BackendClient


load_dotenv()

class Main:
    
    enabled: bool
    secondToRetry: int
    client: BackendClient
    
    def start(self) -> None:
        
        self.client = BackendClient(
            os.getenv('BACKEND_URL') or '',
            os.getenv('SECONDS_TO_RETRY') or '30',
            os.getenv('API_TOKEN') or None
        )

        self.enabled = True
        self.secondToRetry = 30
        while self.enabled:
            print('2 seconds passed')
            sleep(2)