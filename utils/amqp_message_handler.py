from typing import Callable


class AMQPMessageHandler:

    all_data: list[dict]
    active_data: list[dict]
    active_callback: Callable
    removed_callback: Callable
    
    def __init__(self, active_callback: Callable, removed_callback: Callable) -> None:
        self.active_callback = active_callback
        self.removed_callback = removed_callback

    def handle(self, all_data: list, active_data: list, type: str, data: dict) -> tuple[list, list]:
        self.all_data = all_data
        self.active_data = active_data
        if type == 'App\\Messenger\\Message\\EnableGPSFakeMessage':
            return self.__handle_activity(data)
        if type == 'App\\Messenger\\Message\\FakeGPSCrudMessage':
            match data["operation"]:
                case "CREATE":
                    return self.__handle_creation(data)
                case "UPDATE":
                    return self.__handle_update(data)
                case "DELETE":
                    return self.__handle_deletion(data)
        return self.all_data, self.active_data
        

    def __handle_activity(self, data: dict) -> tuple[list, list]:
        print("ACTIVITY")
        print(self.all_data[0].keys())
        added = data["added"]
        removed = data["removed"]
        for ac_data in self.active_data:
            if ac_data['code'] in removed:
                self.active_data.remove(ac_data)
                self.removed_callback(ac_data)
        for datum in self.all_data:
            if datum['code'] in added:
                self.active_data.append(datum)
                self.active_callback(datum)
        return self.all_data, self.active_data
    
    def __handle_creation(self, data: dict) -> tuple[list, list]:
        print("CREATED")
        self.all_data.append({
            "code": data["code"],
            "coordinates": data["locations"],
        })
        return self.all_data, self.active_data
    
    def __handle_deletion(self, data: dict) -> tuple[list, list]:
        print("DELETED")
        all_data = [a for a in self.all_data if a["code"] != data["code"]]
        active_data = [a for a in self.active_data if a["code"] != data["code"]]
        return all_data, active_data
    
    def __handle_update(self, data: dict) -> tuple[list, list]:
        print("UPDATED")
        self.all_data = [a for a in self.all_data if a["code"] != data["code"]]
        self.all_data.append({
            "code": data["code"],
            "coordinates": data["locations"],
        })
        self.active_data = [a for a in self.active_data if a["code"] != data["code"]]
        self.active_data.append({
            "code": data["code"],
            "coordinates": data["locations"],
        })
        return self.all_data, self.active_data