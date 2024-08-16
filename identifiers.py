import dearpygui.dearpygui as dpg

import logging

logger = logging.getLogger(__name__)

WINDOW_ID = dpg.generate_uuid()
ABOUT_WINDOW_ID = dpg.generate_uuid()

PREVIEW_TAB_ID = dpg.generate_uuid()
SELECTION_TAB_ID = dpg.generate_uuid()
VIEWER_TAB_ID = dpg.generate_uuid()

PREVIEW_TAB_BUTTON_ID = dpg.generate_uuid()
SELECTION_TAB_BUTTON_ID = dpg.generate_uuid()
VIEWER_TAB_BUTTON_ID = dpg.generate_uuid()
COUNTER_TAB_TEXT_ID = dpg.generate_uuid()

PREVIEW_MENU_ITEM_ID = dpg.generate_uuid()
SELECTION_MENU_ITEM_ID = dpg.generate_uuid()
VIEWER_MENU_ITEM_ID = dpg.generate_uuid()
SIMPLE_PREVIEW_MENU_ITEM_ID = dpg.generate_uuid()
SCALE_MENU_ITEM_ID = dpg.generate_uuid()

SCALE_TEXT_ID = dpg.generate_uuid()

SELECTION_CHILD_ID = dpg.generate_uuid()

PREVIEW_PLOT_ID = dpg.generate_uuid()

PREVIEW_IMAGE1_ID = dpg.generate_uuid()
PREVIEW_IMAGE2_ID = dpg.generate_uuid()
VIEWER_IMAGE_ID = dpg.generate_uuid()

PREVIEW_TEXT_INFO_ID = dpg.generate_uuid()
VIEWER_TEXT_INFO_ID = dpg.generate_uuid()
VIEWER_TEXT_DATA_ID = dpg.generate_uuid()

ANALYSIS_INDICATOR_ID = dpg.generate_uuid()
BUTTON_SHOW_RESULT = dpg.generate_uuid()
TEXTURE_SHOW_RESULT = dpg.generate_uuid()

FPS_DEBUG_TEXT_ID = dpg.generate_uuid()
IDS_DEBUG_TEXT_ID = dpg.generate_uuid()

class IdGenerator:
    def __init__(self) -> None:
        self.free_identifiers = set()
        self.active_identifiers = set()

    def release_id(self, *ids: int) -> None:
        self.active_identifiers.difference_update(ids)
        self.free_identifiers.update(ids)
    
    def generate_id(self) -> int:
        if 0:#self.free_identifiers: # FIX
            id = self.free_identifiers.pop()
        else:
            id = dpg.generate_uuid()
        self.active_identifiers.add(id)
        return id
    
    def add_active_id(self, id: int) -> None:
        self.free_identifiers.discard(id)
        self.active_identifiers.add(id)
