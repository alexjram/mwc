import json
from typing import Callable, Union

from utils.data_processor import DataProcessor


class FileParser:
    whole_data: list
    active_data: list
    
    def __init__(self, path: str):
        self.path = path

    def load_json(self) -> list:
        with open(self.path, 'r') as file:
            data = json.load(file)
        file.close()
        self.whole_data = DataProcessor.normalize(data)
        self.active_data = []
        return data
    
    def filter_active(self, added: list[str], removed: list[str], active_callback: Union[Callable, None] = None, removed_callback: Union[Callable, None] = None) -> list[dict]:
        active_data = self.active_data.copy()
        
        for ac_data in self.active_data:
            if ac_data['code'] in removed:
                active_data.remove(ac_data)
                if removed_callback is not None:
                    removed_callback(ac_data)
        for datum in self.whole_data:
            if datum['code'] in added:
                active_data.append(datum)
                if active_callback is not None:
                    active_callback(datum)
        self.active_data = active_data
        return active_data