import base64
import os

from manager.base_manager import BaseManager

def time_convert(time: str) -> int:
    seconds = 0
    time_parts = time.split(':')
    seconds = int(time_parts[0]) * 60 + int(time_parts[1])
    return seconds

def read_document(document) -> None|bytes:
    if not os.path.isfile(document):
        return None

    with open(document, 'rb') as file:
        return file.read()
    
def to_base64(document) -> None|str:
    bytes_read = read_document(document)
    if not bytes_read:
        return None

    return base64.b64encode(bytes_read).decode()

def loop_until_is_done(manager: BaseManager, callback: callable) -> None:
    sent = False
    while not sent:
        try:
            callback()
            sent = True
        except Exception as e:
            if e.args[0] != "SERVER_OFF":
                manager.event.set()
                return
            
            manager.client.check_if_server_is_up()

