import dearpygui.dearpygui as dpg

from queue import Queue

from typing import Callable

import logging

logger = logging.getLogger(__name__)


# Actions
ADD_ACTION = 0
DELETE_ACTION = 1
CONFIGURE_ACTION = 2
COMMANDS_ACTION = 3

# item types
item_types = {
    "image_button": dpg.add_image_button,
    "button": dpg.add_button,
    "text": dpg.add_text,
    "tooltip": dpg.add_tooltip,
    "loading_indicator": dpg.add_loading_indicator,
}


class DpgWrapper:
    """ - dearpygui (dpg) обертка, 
    сделана с целью оптимизации и отказа от обращения
    к dpg во второстепенном потоке, что является плохой практикой)"""
    def __init__(self) -> None:
        self.tasks_queue = Queue()

    def add_item(self, item_type_: str, **kwargs) -> None:
        self.tasks_queue.put((ADD_ACTION, item_type_, kwargs))

    def delete_item(self, item: int | str, **kwargs) -> None:
        self.tasks_queue.put((DELETE_ACTION, item, kwargs))

    def configure_item(self, item: int | str, **kwargs) -> None:
        self.tasks_queue.put((CONFIGURE_ACTION, item, kwargs))

    def dpg_command(self, command: Callable, **kwargs) -> None:
        self.tasks_queue.put((COMMANDS_ACTION, command, kwargs))

    def _update_dpg(self, action: int, target: str | int | Callable, **kwargs) -> None:
        if action == ADD_ACTION:
            if target in item_types.keys():
                item_types[target](**kwargs)
            else:
                logger.error(f"Не найден тип элемента: {target}")
        elif action == DELETE_ACTION:
            try:
                dpg.delete_item(target, **kwargs)
            except SystemError:
                logger.error(f"Ошибка удаления: {target}")
        elif action == CONFIGURE_ACTION:
            try:
                dpg.configure_item(target, **kwargs)
            except Exception as e:
                logger.error(f"Ошибка конфигурирования: {target}\n{str(e)}")
        elif action == COMMANDS_ACTION:
            try:
                target(**kwargs)
            except Exception as e:
                logger.error(f"Ошибка выполнения команды: {str(e)}")

    def update_dpg(self) -> None:
        try:
            while not self.tasks_queue.empty():
                action, target, kwargs = self.tasks_queue.get()
                self._update_dpg(action, target, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка обработки очереди: {str(e)}")

