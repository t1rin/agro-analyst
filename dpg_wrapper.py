import dearpygui.dearpygui as dpg

from queue import Queue

import logging

logger = logging.getLogger(__name__)


# Actions
ADD_ACTION = 0
DELETE_ACTION = 1
CONFIGURE_ACTION = 2

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

    def _update_dpg_item(self, action: int, item: str | int, **kwargs) -> None:
        if action == ADD_ACTION:
            if item in item_types.keys():
                item_types[item](**kwargs)
            else:
                logger.error(f"Не найден тип элемента: {item}")
        elif action == DELETE_ACTION:
            try:
                dpg.delete_item(item, **kwargs)
            except SystemError:
                logger.error(f"Ошибка удаления: {item}")
        elif action == CONFIGURE_ACTION:
            try:
                dpg.configure_item(item, **kwargs)
            except Exception as e:
                logger.error(f"Ошибка конфигурирования: {item}\n{str(e)}")

    def update_dpg(self) -> None:
        try:
            while not self.tasks_queue.empty():
                action, item, kwargs = self.tasks_queue.get()
                self._update_dpg_item(action, item, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка обработки очереди: {str(e)}")

