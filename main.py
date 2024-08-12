import asyncio, time
import dearpygui.dearpygui as dpg

import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s][%(asctime)s] - %(name)s - %(message)s',
                    datefmt='%H:%M:%S')

logger = logging.getLogger(__name__)

dpg.create_context()

from analyzer import *

from config import *
from templates import *
from identifiers import *
from theme_settings import *
from utils import *


analysis_results = {}
scale = 1

free_identifiers = []

async def conditions_loop() -> None:
    ...
    # await check_images_dir()
    # await check_results_dir()

async def check_images_dir() -> None:
    images_json_file = "./data/images/images.json"
    data_images = await asyncio.to_thread(json_read, images_json_file)

    if not data_images:
        if data_images is None:
            await asyncio.to_thread(json_write, images_json_file)
        return
    
    await asyncio.to_thread(json_write, images_json_file)

    for name, data in data_images.items():
        img_name = "./data/images/" + name
        asyncio.create_task(image_analysis(img_name, data))

def change_tab_callback(_, __, widget_id: int):
    asyncio.run(change_tab(widget_id))

def fullscreen_callback(sender: int, __) -> None:
    dpg.toggle_viewport_fullscreen() # TODO
    logger.info("Кнопка " + MENU_BAR["view"]["full_screen"] + " была активирована")

def simple_preview_callback(_, __) -> None:
    simple_preview = dpg.get_value(SIMPLE_PREVIEW_MENU_ITEM_ID)
    dpg.configure_item(PREVIEW_IMAGE2_ID, show=(simple_preview))
    dpg.configure_item(PREVIEW_PLOT_ID, show=(not simple_preview))
    logger.info(
        "Выбран простой режим просмотра " if simple_preview
        else "Выбран стандартный режим просмотра"
    )

def scale_callback(sender: int, __) -> None:
    global scale
    scale = dpg.get_value(sender)

    global analysis_results
    results = list(analysis_results.keys())
    # delete_results_textures()
    # load_results_textures(results)

def close_all_on_exit() -> None:
    dpg.delete_item(WINDOW_ID, children_only=True)
    dpg.delete_item(WINDOW_ID)
    dpg.stop_dearpygui()
    logger.info("Программа успешно завершена.")

async def change_tab(widget_id: int) -> None:
    dpg.hide_item(PREVIEW_TAB_ID)
    dpg.hide_item(SELECTION_TAB_ID)
    dpg.hide_item(VIEWER_TAB_ID)
    dpg.show_item(widget_id)

    dpg.bind_item_theme(PREVIEW_TAB_BUTTON_ID, global_theme)
    dpg.bind_item_theme(SELECTION_TAB_BUTTON_ID, global_theme)
    dpg.bind_item_theme(VIEWER_TAB_BUTTON_ID, global_theme)
    replaces = {PREVIEW_TAB_ID: PREVIEW_TAB_BUTTON_ID,
                SELECTION_TAB_ID: SELECTION_TAB_BUTTON_ID,
                VIEWER_TAB_ID: VIEWER_TAB_BUTTON_ID}
    dpg.bind_item_theme(replaces[widget_id], active_tab_button_theme)

    # delete_results_textures()

    await update_menu_bar()

async def update_menu_bar() -> None:
    main_tab_is_shown = dpg.is_item_shown(PREVIEW_TAB_ID)
    dpg.set_value(PREVIEW_MENU_ITEM_ID, main_tab_is_shown)
    selection_tab_is_shown = dpg.is_item_shown(SELECTION_TAB_ID)
    dpg.set_value(SELECTION_MENU_ITEM_ID, selection_tab_is_shown)
    viewer_tab_is_shown = dpg.is_item_shown(VIEWER_TAB_ID)
    dpg.set_value(VIEWER_MENU_ITEM_ID, viewer_tab_is_shown)
    
    dpg.configure_item(item=SIMPLE_PREVIEW_MENU_ITEM_ID,
                       show=main_tab_is_shown)
    
    dpg.configure_item(item=SCALE_MENU_ITEM_ID,
                       show=selection_tab_is_shown)

async def create_menu_bar() -> None:
    with dpg.menu_bar():
        with dpg.menu(label=MENU_BAR["menus"]["view"]):
            dpg.bind_item_font(dpg.last_item(), menu_font)
            dpg.add_menu_item(label=MENU_BAR["view"]["preview"], check=True, default_value=True, 
                callback=change_tab_callback, tag=PREVIEW_MENU_ITEM_ID, user_data=PREVIEW_TAB_ID)
            dpg.add_menu_item(label=MENU_BAR["view"]["selection"], check=True,
                callback=change_tab_callback, tag=SELECTION_MENU_ITEM_ID, user_data=SELECTION_TAB_ID)
            dpg.add_menu_item(label=MENU_BAR["view"]["viewer"], check=True,
                callback=change_tab_callback, tag=VIEWER_MENU_ITEM_ID, user_data=VIEWER_TAB_ID)
            dpg.add_separator()
            dpg.add_menu_item(label=MENU_BAR["view"]["full_screen"], check=True, callback=fullscreen_callback)
        with dpg.menu(label=MENU_BAR["menus"]["options"]):
            dpg.bind_item_font(dpg.last_item(), menu_font)
            dpg.add_menu_item(label=MENU_BAR["options"]["simple_preview"], default_value=DEFAULT_SIMPLE_PREVIEW,
                callback=simple_preview_callback, check=True, tag=SIMPLE_PREVIEW_MENU_ITEM_ID)
            dpg.add_menu(label=MENU_BAR["options"]["scale"], tag=SCALE_MENU_ITEM_ID, show=False)
            dpg.add_slider_float(parent=dpg.last_item(), callback=scale_callback,
                min_value=0.2, max_value=10, default_value=1, width=30, format="%.1f", vertical=True)

async def create_tab_bar() -> None:
    with dpg.child_window(autosize_x=True, show=SHOW_TAB_BAR, height=46): # HACK
        with dpg.group(horizontal=True):
            dpg.add_button(label=MENU_BAR["view"]["preview"], 
                callback=change_tab_callback, user_data=PREVIEW_TAB_ID,
                tag=PREVIEW_TAB_BUTTON_ID)
            dpg.add_button(label=MENU_BAR["view"]["selection"], 
                callback=change_tab_callback, user_data=SELECTION_TAB_ID,
                tag=SELECTION_TAB_BUTTON_ID)
            dpg.add_button(label=MENU_BAR["view"]["viewer"], 
                callback=change_tab_callback, user_data=VIEWER_TAB_ID,
                tag=VIEWER_TAB_BUTTON_ID)
            dpg.add_text()

async def init_interface() -> None:
    with dpg.window(tag=WINDOW_ID):
        await create_menu_bar()
        await create_tab_bar()
        with dpg.group():
            with dpg.group(tag=PREVIEW_TAB_ID):
                with dpg.table(header_row=False, hideable=True, resizable=True):
                    dpg.add_table_column()
                    dpg.add_table_column(width_fixed=True, 
                        init_width_or_weight=DEFAULT_PANEL_WIDTH)
                    with dpg.table_row():
                        with dpg.child_window():
                            with dpg.plot(width=-1, height=-1, equal_aspects=True, no_mouse_pos=True, 
                                            no_menus=True, show=(not DEFAULT_SIMPLE_PREVIEW), tag=PREVIEW_PLOT_ID):
                                options = {"no_gridlines": True, "no_tick_marks": True, "no_tick_labels": True}
                                dpg.add_plot_axis(dpg.mvXAxis, **options) 
                                with dpg.plot_axis(dpg.mvYAxis, **options):
                                    texture = create_texture(tag=TEXTURE_SHOW_RESULT)
                                    dpg.add_image_series(texture, [0, 0], [0, 0], tag=PREVIEW_IMAGE1_ID)
                            dpg.add_image(
                                texture_tag=create_texture(),
                                tag=PREVIEW_IMAGE2_ID,
                                show=DEFAULT_SIMPLE_PREVIEW
                            )
                        with dpg.child_window():
                            with dpg.collapsing_header(label="Данные", default_open=True):
                                dpg.add_text(format_text(TEXT_INFO_PANEL), 
                                    tag=PREVIEW_TEXT_INFO_ID, indent=8, wrap=0)
                            with dpg.collapsing_header(label="Анализ", default_open=True):
                                with dpg.group(horizontal=True):
                                    dpg.add_loading_indicator(tag=ANALYSIS_INDICATOR_ID, show=False)
                                    dpg.add_image_button(
                                        create_texture(),
                                        tag=BUTTON_SHOW_RESULT,
                                        #callback=show_result,
                                        show=False,
                                    )
            with dpg.group(tag=SELECTION_TAB_ID):
                with dpg.child_window():
                    with dpg.child_window(tag=SELECTION_CHILD_ID):
                        dpg.bind_item_theme(dpg.last_item(), selection_theme)
            with dpg.group(tag=VIEWER_TAB_ID):
                with dpg.table(header_row=False, hideable=True, resizable=True):
                    dpg.add_table_column(width_fixed=True, 
                        init_width_or_weight=DEFAULT_PANEL_WIDTH)
                    dpg.add_table_column()
                    with dpg.table_row():
                        with dpg.child_window():
                            with dpg.collapsing_header(label="Информация о снимке", default_open=True):
                                dpg.add_text(format_text(TEXT_INFO_PANEL), 
                                    tag=VIEWER_TEXT_INFO_ID, indent=8, wrap=0)
                            with dpg.collapsing_header(label="Данные", default_open=True):
                                dpg.add_text(format_text(TEXT_DATA_PANEL), 
                                    tag=VIEWER_TEXT_DATA_ID, indent=8, wrap=0)
                            with dpg.collapsing_header(label="Статус", default_open=True):
                                ...
                        with dpg.child_window():
                            with dpg.plot(width=-1, height=-1, equal_aspects=True, 
                                          no_mouse_pos=True, no_menus=True):
                                options = {"no_tick_labels": True}
                                dpg.add_plot_axis(dpg.mvXAxis, **options) 
                                with dpg.plot_axis(dpg.mvYAxis, **options):
                                    dpg.add_image_series(
                                        create_texture(),
                                        [0, 0], [0, 0],
                                        tag=VIEWER_IMAGE_ID,
                                    )
        
        # dpg.delete_item(TAB_BAR_ID) # TODO: показ вверху или внизу
        # create_tab_bar()

    await change_tab(PREVIEW_TAB_ID)

async def main_loop() -> None:
    interval = 1 / UPDATING_RATE
    time_stamp = time.time()
    while dpg.is_dearpygui_running():
        if time.time() - time_stamp >= interval:
            asyncio.create_task(conditions_loop())
            time_stamp = time.time()
        dpg.render_dearpygui_frame()

if __name__ == "__main__":
    logger.info("Initialization...")

    dpg.create_viewport(**VIEWPORT_OPTIONS)
    dpg.set_viewport_max_height(MAX_HEIGHT)
    dpg.set_viewport_max_width(MAX_WIDTH)
    dpg.set_viewport_min_height(MIN_HEIGHT)
    dpg.set_viewport_min_width(MIN_WIDTH)

    dpg.bind_theme(global_theme)
    dpg.bind_font(global_font)

    asyncio.run(init_interface())

    dpg.set_exit_callback(close_all_on_exit)

    dpg.set_primary_window(WINDOW_ID, True)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    
    asyncio.run(main_loop())

dpg.destroy_context()
