from requests import get
from utils.time_converter import convert_time_to_int


class DataProcessor:
    @staticmethod
    def normalize(data: list[dict]) -> list[dict]:
        new_data = []
        for datum in data:
            total_time = 0
            locations = []
            coordinates = datum.get('coordinates', [])
            if len(coordinates) == 0:
                coordinates = datum.get('locations', [])
                
            for location in coordinates:
                total_time = convert_time_to_int(location.get('time', '00:00'))
                locations.append({
                    "time": location.get('time', '00:00'),
                    "latitude": location.get('latitude', 0),
                    "longitude": location.get('longitude', 0),
                    "altitude": location.get('altitude', 0),
                    "seconds": total_time,
                    "image": location.get('image', None),
                    "content": location.get('content', None)
                })
            new_data.append({
                'type': datum.get('type', 'default'),
                'code': datum.get('code', ''),
                'coordinates': locations,
                'events': datum.get('events', []),
                'total_time': total_time,
                'streamer': None,
                'refresh': datum.get('refresh', None),
                'endpoint': datum.get('endpoint', None),
                'input': datum.get('input', None),
                'output': datum.get('output', None),
                'streamer': None
            })
        return new_data
    
    