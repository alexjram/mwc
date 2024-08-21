from manager.base_manager import BaseManager

from manager.main_manager import MainManager
from manager.with_endpoint_manager import WithEndpointManager
from manager.with_image_manager import WithImageManager

def get_manager_by_type(type = 'default') -> BaseManager:
    return {
        'default': MainManager,
        'with_endpoint': WithEndpointManager,
        'with_image': WithImageManager,
    }.get(type, MainManager)
