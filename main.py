import dearpygui.dearpygui as dpg

dpg.create_context()

from config import *
from identifiers import *
from utils import *

dpg.create_viewport(**VIEWPORT_OPTIONS)
dpg.set_viewport_max_height(MAX_HEIGHT)
dpg.set_viewport_max_width(MAX_WIDTH)
dpg.set_viewport_min_height(MIN_HEIGHT)
dpg.set_viewport_min_width(MIN_WIDTH)

class agroAnalyst:
    def __init__(self):
        with dpg.window(**WINDOW_OPTIONS, tag=WINDOW_ID):
            dpg.add_text("Hello, world")

application = agroAnalyst()

dpg.setup_dearpygui()
dpg.show_viewport()

dpg.set_primary_window(WINDOW_ID, True)

dpg.start_dearpygui()
dpg.destroy_context()
