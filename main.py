import dearpygui.dearpygui as dpg

dpg.create_context()

from analyzer import *

from config import *
from identifiers import *
from theme_settings import *
from utils import *

dpg.create_viewport(**VIEWPORT_OPTIONS)
dpg.set_viewport_max_height(MAX_HEIGHT)
dpg.set_viewport_max_width(MAX_WIDTH)
dpg.set_viewport_min_height(MIN_HEIGHT)
dpg.set_viewport_min_width(MIN_WIDTH)


def create_menu_bar() -> None:
    with dpg.menu_bar():
        with dpg.menu(label=MENU_BAR["menus"]["view"]):
            dpg.add_menu_item(label=MENU_BAR["view"]["main"], check=True, default_value=True, 
                callback=change_tab, tag=MAIN_MENU_ITEM_ID, user_data=MAIN_TAB_ID)
            dpg.add_menu_item(label=MENU_BAR["view"]["selection"], check=True,
                callback=change_tab, tag=SELECTION_MENU_ITEM_ID, user_data=SELECTION_TAB_ID)
            dpg.add_menu_item(label=MENU_BAR["view"]["viewer"], check=True,
                callback=change_tab, tag=VIEWER_MENU_ITEM_ID, user_data=VIEWER_TAB_ID)

def update_menu_bar() -> None:
    main_tab_is_shown = dpg.is_item_shown(MAIN_TAB_ID)
    dpg.set_value(MAIN_MENU_ITEM_ID, main_tab_is_shown)
    selection_tab_is_shown = dpg.is_item_shown(SELECTION_TAB_ID)
    dpg.set_value(SELECTION_MENU_ITEM_ID, selection_tab_is_shown)
    viewer_tab_is_shown = dpg.is_item_shown(VIEWER_TAB_ID)
    dpg.set_value(VIEWER_MENU_ITEM_ID, viewer_tab_is_shown)

def change_tab(_, __, widget_id) -> None:
    dpg.hide_item(MAIN_TAB_ID)
    dpg.hide_item(SELECTION_TAB_ID)
    dpg.hide_item(VIEWER_TAB_ID)
    dpg.show_item(widget_id)
    update_menu_bar()

def create_tab_bar() -> None:
    with dpg.child_window(autosize_x=True, height=42): # HACK
        with dpg.group(horizontal=True):
            dpg.add_button(label=MENU_BAR["view"]["main"], 
                callback=change_tab, user_data=MAIN_TAB_ID)
            dpg.add_button(label=MENU_BAR["view"]["selection"], 
                callback=change_tab, user_data=SELECTION_TAB_ID)
            dpg.add_button(label=MENU_BAR["view"]["viewer"], 
                callback=change_tab, user_data=VIEWER_TAB_ID)
            dpg.add_text()

def begin() -> None:
    with dpg.window(tag=WINDOW_ID):
        create_menu_bar()
        if SHOW_TAB_BAR:
            create_tab_bar()
        with dpg.group():
            with dpg.group(tag=MAIN_TAB_ID):
                with dpg.table(header_row=False, hideable=True, resizable=True):
                    dpg.add_table_column()
                    dpg.add_table_column(
                        width_fixed=True, init_width_or_weight=DEFAULT_PANEL_WIDTH)
                    with dpg.table_row():
                        with dpg.child_window():
                            ...
                        with dpg.child_window():
                            ...
            with dpg.group(tag=SELECTION_TAB_ID, show=False):
                with dpg.child_window():
                    ...
            with dpg.group(tag=VIEWER_TAB_ID, show=False):
                with dpg.table(header_row=False, hideable=True, resizable=True):
                    dpg.add_table_column(
                        width_fixed=True, init_width_or_weight=DEFAULT_PANEL_WIDTH)
                    dpg.add_table_column()
                    with dpg.table_row():
                        with dpg.child_window():
                            ...
                        with dpg.child_window():
                            ...
        
        # dpg.delete_item(TAB_BAR_ID) # TODO: показ вверху или внизу
        # tab_bar()


if CUSTOM_THEME:
    dpg.bind_theme(global_theme)
if CUSTOM_FONT:
    dpg.bind_font(global_font)

begin()

dpg.set_primary_window(WINDOW_ID, True)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
