import grequests
from typing import Union
import requests
import json
from time import sleep, time

class BackendClient:
    url: str
    seconds_to_retry: int
    api_token: Union[str, None]
    xrf_token: Union[str, None]
    xrf_refresh_token: Union[str, None]
    
    def __init__(self, url: str, seconds_to_retry: str, api_token: str|None) -> None:
        self.url = url
        self.seconds_to_retry = int(seconds_to_retry)
        self.api_token = api_token
        
    def set_xrf_auth(self, username: str, password: str) -> None:
        request = requests.post(
            self.url + '/api/login_check',
            json={
                'username': username,
                'password': password
            }
        )
        if request.status_code != 200:
            raise Exception("invalid credentials")
        json_data = request.json()
        self.xrf_token = json_data.get('token', None)
        self.xrf_refresh_token = json_data.get('refresh_token', None)
        
    def refresh_token(self) -> None:
        request = requests.post(
            self.url + '/api/refresh_token',
            json={
                'refresh_token': self.xrf_refresh_token
            }
        )
        if request.status_code != 200:
            raise Exception("invalid refresh token")
        json_data = request.json()
        self.xrf_token = json_data.get('token', None)
        self.xrf_refresh_token = json_data.get('refresh_token', None)

    def build_headers(self) -> dict:
        if self.api_token:
            return {
                'Authorization': f"Bearer {self.api_token}",
            }
        
        return {}

    def send_post(self, endpoint: str, payload: dict = {}, headers: dict = {}, files: dict = {}, data: dict = {}) -> None:
        url = self.url + endpoint

        try:
            res = requests.post(url, json=payload, headers=headers, files=files, data=data)
        except Exception as e:
            print(f"Unable to establish connection with {url}. Error: {e}")
            raise Exception("SERVER_OFF")
        
        print(res.status_code)

        if res.status_code != 201:
            print(res.json())
            raise Exception(f"invalid item for {endpoint}")

    def check_if_server_is_up(self, url = None) -> None:
        url = (self.url + '/api') if url is None else url

        isUp = False
        while not isUp: 
            try:
                requests.options(url)
                isUp = True
            except Exception as e:
                print(f"Unable to establish connection. Error: {e}. Next retry in {self.seconds_to_retry} seconds")
                sleep(self.seconds_to_retry)

    def send_location(self, latitude: float, longitude: float, code: str, altitude: float = 0, rel_altitude: float = 0) -> None:
        payload = {
            "emergency": False,
            "latitude": latitude,
            "longitude": longitude,
            "assetCode": code,
            "azimuth": None,
            "altitude": altitude,
            "relAltitude": rel_altitude,
            "precision": 0,
        }
        
        endpoint = '/api/location_logs'
        self.send_post(endpoint, payload)
        
    def send_alert(self, content_id: str, events: dict, image: bytes) -> None:
        data = {
            "content_id": content_id,
            "events": json.dumps(events),
            "datetime": int(time()),
        }
        
        files = {'image': image}
        headers = self.build_headers()
        endpoint = '/api/external/alerts/ai'

        self.send_post(endpoint, headers=headers, files=files, data=data)
        
    def send_alert_async(self, content_id: str, events: dict, image: bytes) -> None:
        data = {
            "content_id": content_id,
            "events": json.dumps(events),
            "datetime": int(time())
        }
        
        files = {'image': image}
        headers = self.build_headers()
        endpoint = '/api/external/alerts/ai'
        def res_request(res):
            print(res)
        req = grequests.post(self.url + endpoint, headers=headers, files=files, data=data, hooks=res_request)
        grequests.send(req, grequests.Pool(1))
        
    def external_request(self, endpoint: str, method: str, to_json: bool = True) -> Union[dict, str]:
        
        try:
            res = requests.request(
                method=method,
                url=endpoint,
            )
        except Exception as e:
            print(f"Unable to establish connection with {endpoint}. Error: {e}")
            raise Exception("SERVER_OFF")
        
        return res.json() if to_json else res.text
    
    def save_logs_batch(self, logs: list) -> None:
        data = {
            "locations": logs
        }
        request = requests.post(f"{self.url}/api/location_logs/batch", json=data, headers={
            "Authorization": f"Bearer {self.xrf_token}"
        })
        if request.status_code == 401:
            self.refresh_token()
            self.save_logs_batch(logs)
        
        

        
            
