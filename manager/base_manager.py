from abc import ABC, abstractmethod
from threading import Event, Thread
from backend_client import BackendClient

class BaseManager(ABC):

    event: Event
    thread: Thread
    client: BackendClient

    def __init__(self, client: BackendClient, data: dict) -> None:
        self.event = Event()
        self.client  = client
        self.start(data)

    @abstractmethod
    def print(self, message) -> None:
        pass

    @abstractmethod
    def start(self, data: dict):
        pass

    @abstractmethod
    def stop(self) -> None:
        self.event.set()
        self.thread.join()
        self.print('Stopped thread')
