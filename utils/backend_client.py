from typing import Union
import requests
import json
from time import sleep, time
import aiohttp
import asyncio


class BackendClient:
    url: str
    seconds_to_retry: int
    api_token: Union[str, None]
    xrf_token: Union[str, None]
    xrf_refresh_token: Union[str, None]
    timeout: aiohttp.ClientTimeout
    
    def __init__(self, url: str, seconds_to_retry: str, api_token:Union[str, None]) -> None:
        self.url = url
        self.seconds_to_retry = int(seconds_to_retry)
        self.api_token = api_token
        self.timeout = aiohttp.ClientTimeout(total=5)
        
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
        
    def send_location_async(self, latitude: float, longitude: float, code: str, altitude: float = 0, rel_altitude: float = 0, is_loop_executing = False):
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
        async def send():
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post( self.url + endpoint, json=payload) as resp:
                    print("status: ", resp.status)
        if not is_loop_executing:
            asyncio.run(send())
        else :
            return send
        
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
        
    def send_alert_async(self, content_id: str, events: dict, image: str) -> None:
        print(image)
        data = {
            "content_id": content_id,
            "events": json.dumps(events),
            "datetime": f"{int(time())}",
            "image": open(image, 'rb')
        }
        
        headers = {
            "Authorization": f"Bearer {self.xrf_token}"
        }
        endpoint = '/api/alerts/ai'
        async def send():
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post( self.url + endpoint, headers=headers, data=data) as resp:
                    print("status: ", resp.status)
        asyncio.run(send())
        
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
    def external_request_async(self, endpoint: str, method: str, code: str) -> None:
        try:
            async def send():
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.request( method, endpoint, headers={"Content-Type": "application/json"}) as resp:
                        print("status: ", resp.status)
                        
                        if resp.status == 200:
                            if resp.content_type == "application/json":
                                data = await resp.json()
                            else:
                                data = await resp.text()
                                data = json.loads(data)
                            print(data)
                    new_data = {
                        "code": code,
                        "latitude": data['latLng'].split(',')[0],
                        "longitude": data['latLng'].split(',')[1],
                        "altitude": 0,
                        "relAltitude": 0,
                        "precision": 0,
                        "emergency": False
                    }
                    async with session.post( self.url + '/api/location_logs', json=new_data) as resp2:
                        print("status: ", resp.status)
            asyncio.run(send())
        except Exception as e:
            print(f"Unable to establish connection with {endpoint}. Error: {e}")
            raise Exception("SERVER_OFF")
    def save_logs_batch(self, logs: list[dict]) -> None:
        data = {
            "locations": logs
        }
        request = requests.post(f"{self.url}/api/location_logs/batch", json=data, headers={
            "Authorization": f"Bearer {self.xrf_token}"
        })
        if request.status_code == 401:
            self.refresh_token()
            self.save_logs_batch(logs)
        else:
            print(f"save_logs_batch: {request.status_code}")
        
    def get_gps_list(self) -> list[dict]:
        request = requests.get(f"{self.url}/api/fake_gps", headers={
            "Authorization": f"Bearer {self.xrf_token}"
        })
        if request.status_code == 401:
            self.refresh_token()
            return self.get_gps_list()
        else:
            return request.json()
        
        

        
            
