from manager.base_manager import BaseManager

from manager.main_manager import MainManager
from manager.verizon_manager import VerizonManger

def get_manager_by_type(type = 'default') -> BaseManager:
    return {
        'default': MainManager,
        'verizon': VerizonManger,
    }.get(type, MainManager)
