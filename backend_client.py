import requests

class BackendClient:
    url: str
    
    def __init__(self, url: str):
        self.url = url
        
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
        res = requests.post(url, json=payload)
        
        print(res.status_code)
        
        if res.status_code != 201:
            print(res.json())
            raise Exception("invalid location")