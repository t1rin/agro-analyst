import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

dpg.create_context()

from config import *
from identifiers import *
from theme_settings import *
from utils import *

dpg.create_viewport(**VIEWPORT_OPTIONS)
dpg.set_viewport_max_height(MAX_HEIGHT)
dpg.set_viewport_max_width(MAX_WIDTH)
dpg.set_viewport_min_height(MIN_HEIGHT)
dpg.set_viewport_min_width(MIN_WIDTH)

def begin() -> None:
    with dpg.window(tag=WINDOW_ID):
        with dpg.menu_bar():
            ...


        with dpg.table(header_row=False, hideable=True, resizable=True):
            dpg.add_table_column()
            dpg.add_table_column(width_fixed=True, 
                                 init_width_or_weight=DEFAULT_PANEL_WIDTH)

            with dpg.table_row():
                with dpg.child_window():
                    ...
                with dpg.child_window():
                    ...


if CUSTOM_THEME:
    dpg.bind_theme(global_theme)
if CUSTOM_FONT:
    ... # TODO
    # dpg.bind_font(font)

begin()

dpg.set_primary_window(WINDOW_ID, True)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
