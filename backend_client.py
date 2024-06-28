import requests
from time import sleep

class BackendClient:
    url: str
    secondsToRetry: int
    
    def __init__(self, url: str, secondsToRery: str):
        self.url = url
        self.secondsToRetry = int(secondsToRery)

    def check_if_server_is_up(self) -> None:
        url = self.url + '/api'

        isUp = False
        while not isUp: 
            try:
                requests.options(url)
                isUp = True
            except Exception as e:
                print(f"Unable to establish connection. Error: {e}. Next retry in {self.secondsToRetry} seconds")
                sleep(self.secondsToRetry)

    def send_location(self, latitude: float, longitude: float, code: str) -> None:
        payload = {
            "emergency": False,
            "latitude": latitude,
            "longitude": longitude,
            "assetCode": code,
            "azimuth": None,
            "altitude": 0,
            "relAltitude": 0,
            "precision": 0,
        }
        
        url = self.url + '/api/location_logs'

        try:
            res = requests.post(url, json=payload)
        except Exception as e:
            print(f"Unable to establish connection with {url}. Error: {e}")
            raise Exception("SERVER_OFF")
        
        print(res.status_code)

        if res.status_code != 201:
            print(res.json())
            raise Exception("invalid location")