import json
import os
import random
import string
from time import sleep
from dotenv import load_dotenv
from backend_client import BackendClient
from thread_manager import ThreadManager


load_dotenv()

class Main:
    client: BackendClient
    threads: dict[str, ThreadManager]
    enabled: bool
    
    def start(self) -> None:
        
        self.client = BackendClient(os.getenv('BACKEND_URL') or '')
        self.threads:dict[str, ThreadManager] = {}
        self.enabled = True
        file = open(os.getenv('DATA_FILE') or '', 'r')
        data = json.load(file)
        file.close()
        
        for obj in data:
            code = obj.get('code', ''.join(random.choices(string.ascii_uppercase, k=6)))
            self.threads[code] = ThreadManager(self.client, obj)
            
        while self.enabled:
            print('2 seconds passed')
            sleep(2)
        
    def stop(self):
        for key in self.threads:
            self.threads[key].stop()
        self.enabled = False
        print('stopped app')

    
if __name__ == '__main__':
    main = Main()
    try:
        main.start()
    except KeyboardInterrupt:
        main.stop()
    