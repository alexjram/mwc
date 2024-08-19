from manager.base_manager import BaseManager

from manager.main_manager import MainManager
from manager.endpoint_manager import EndpointManager

def get_manager_by_type(type = 'default') -> BaseManager:
    return {
        'default': MainManager,
        'endpoint': EndpointManager,
    }.get(type, MainManager)
