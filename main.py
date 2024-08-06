import dearpygui.dearpygui as dpg

from threading import Thread
from time import sleep, time

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

dpg.create_viewport(**VIEWPORT_OPTIONS)
dpg.set_viewport_max_height(MAX_HEIGHT)
dpg.set_viewport_max_width(MAX_WIDTH)
dpg.set_viewport_min_height(MIN_HEIGHT)
dpg.set_viewport_min_width(MIN_WIDTH)


def check_conditions_loop() -> None:
    pause = 1 / 8
    while True:
        check_images_dir()
        check_results_dir()
        sleep(pause)

def check_images_dir() -> None:
    images_json_file = "./data/images/images.json"
    data_images = json_read(images_json_file)
    if not data_images:
        if data_images is None:
            json_write(images_json_file)
        return
    json_write(images_json_file)
    for name, data in data_images.items():
        img_name = "./data/images/" + name
        Thread(target=image_analysis, args=[img_name, data]).start()      

def image_analysis(img_name: str, data: dict) -> None:
    if not file_exists(img_name):
        stamp = time()
        while time() - stamp < 3:
            pass
        if not file_exists(img_name):
            logger.warning(f"Не найден снимок {img_name}")
            return
    
    logger.info(f"Найден новый снимок {img_name}")

    image = load_image(img_name)

    file_delete(img_name)

    height, width = image.shape[:2]
    data_ = convert_to_texture_data(image.copy())

    texture = create_texture(width, height, data_)

    dpg.configure_item(
        item=MAIN_IMAGE1_ID, 
        texture_tag=texture, 
        bounds_min=[0, 0], 
        bounds_max=[width, height]
    )

    dpg.configure_item(MAIN_IMAGE2_ID, texture_tag=texture)

    data_ = NoneDict(data)
    time_ = data_["time"]
    if time_:
        data_["time"] = seconds_to_str(time_)
    data_["width"] = width
    data_["height"] = height

    dpg.set_value(
        PREVIEW_TEXT_INFO_ID,
        format_text(TEXT_INFO_PANEL, data_),
    )
    
    logger.info(f"Снимок {img_name} в обработке")

    segments = segmentation(image)

    analysis_data = {} # TODO

    # for i in range(len(segments)):
    #     analysis_data[i] = ...

    ## saving

    path = "./data/results/" + str(int(time()))

    makedir(path)
    image_record(join_path(path, "source.jpeg"), image)
    for i in range(len(segments)):
        image_record(join_path(path, f"{i}.jpeg"), segments[i])
    json_write(join_path(path, "source_data.json"), data)
    json_write(join_path(path, "analiysis_data.json"), analysis_data)

    logger.info(f"Обработан и сохранён {path}")

def check_results_dir() -> None:
    ...

def simple_preview_callback(_, __) -> None:
    simple_preview = dpg.get_value(SIMPLE_PREVIEW_ITEM_ID)
    dpg.configure_item(MAIN_IMAGE2_ID, show=(simple_preview))
    dpg.configure_item(MAIN_PLOT_ID, show=(not simple_preview))
    logger.info(
        "Выбран простой режим просмотра " if simple_preview
        else "Выбран стандартный режим просмотра"
    )

def create_menu_bar() -> None:
    with dpg.menu_bar():
        with dpg.menu(label=MENU_BAR["menus"]["view"]):
            dpg.bind_item_font(dpg.last_item(), menu_font)
            dpg.add_menu_item(label=MENU_BAR["view"]["preview"], check=True, default_value=True, 
                callback=change_tab, tag=PREVIEW_MENU_ITEM_ID, user_data=PREVIEW_TAB_ID)
            dpg.add_menu_item(label=MENU_BAR["view"]["selection"], check=True,
                callback=change_tab, tag=SELECTION_MENU_ITEM_ID, user_data=SELECTION_TAB_ID)
            dpg.add_menu_item(label=MENU_BAR["view"]["viewer"], check=True,
                callback=change_tab, tag=VIEWER_MENU_ITEM_ID, user_data=VIEWER_TAB_ID)
        with dpg.menu(label=MENU_BAR["menus"]["options"]):
            dpg.bind_item_font(dpg.last_item(), menu_font)
            dpg.add_menu_item(label=MENU_BAR["options"]["simple_preview"], default_value=DEFAULT_SIMPLE_PREVIEW,
                callback=simple_preview_callback, check=True, tag=SIMPLE_PREVIEW_ITEM_ID)

def update_menu_bar() -> None:
    main_tab_is_shown = dpg.is_item_shown(PREVIEW_TAB_ID)
    dpg.set_value(PREVIEW_MENU_ITEM_ID, main_tab_is_shown)
    selection_tab_is_shown = dpg.is_item_shown(SELECTION_TAB_ID)
    dpg.set_value(SELECTION_MENU_ITEM_ID, selection_tab_is_shown)
    viewer_tab_is_shown = dpg.is_item_shown(VIEWER_TAB_ID)
    dpg.set_value(VIEWER_MENU_ITEM_ID, viewer_tab_is_shown)

def change_tab(_, __, widget_id) -> None:
    dpg.hide_item(PREVIEW_TAB_ID)
    dpg.hide_item(SELECTION_TAB_ID)
    dpg.hide_item(VIEWER_TAB_ID)
    dpg.show_item(widget_id)
    update_menu_bar()

def create_tab_bar() -> None:
    with dpg.child_window(autosize_x=True, height=46): # HACK
        with dpg.group(horizontal=True):
            dpg.add_button(label=MENU_BAR["view"]["preview"], 
                callback=change_tab, user_data=PREVIEW_TAB_ID)
            dpg.add_button(label=MENU_BAR["view"]["selection"], 
                callback=change_tab, user_data=SELECTION_TAB_ID)
            dpg.add_button(label=MENU_BAR["view"]["viewer"], 
                callback=change_tab, user_data=VIEWER_TAB_ID)
            dpg.add_text()

def main() -> None:
    logger.info("Initialization...")
    with dpg.window(tag=WINDOW_ID):
        create_menu_bar()
        if SHOW_TAB_BAR:
            create_tab_bar()
        with dpg.group():
            with dpg.group(tag=PREVIEW_TAB_ID):
                with dpg.table(header_row=False, hideable=True, resizable=True):
                    dpg.add_table_column()
                    dpg.add_table_column(width_fixed=True, 
                        init_width_or_weight=DEFAULT_PANEL_WIDTH)
                    with dpg.table_row():
                        with dpg.child_window():
                            with dpg.plot(width=-1, height=-1, equal_aspects=True, no_mouse_pos=True, 
                                            no_menus=True, show=(not DEFAULT_SIMPLE_PREVIEW), tag=MAIN_PLOT_ID):
                                options = {"no_gridlines": True, "no_tick_marks": True, "no_tick_labels": True}
                                dpg.add_plot_axis(dpg.mvXAxis, **options) 
                                with dpg.plot_axis(dpg.mvYAxis, **options):
                                    dpg.add_image_series(
                                        create_texture(),
                                        [0, 0], [0, 0],
                                        tag=MAIN_IMAGE1_ID,
                                    )
                            dpg.add_image(
                                texture_tag=create_texture(),
                                tag=MAIN_IMAGE2_ID,
                                show=DEFAULT_SIMPLE_PREVIEW
                            )
                        with dpg.child_window():
                            with dpg.child_window(border=False):
                                with dpg.collapsing_header(label="Данные", default_open=True):
                                    with dpg.child_window(border=False):
                                        dpg.add_text(format_text(TEXT_INFO_PANEL), 
                                            tag=PREVIEW_TEXT_INFO_ID, indent=8, wrap=0)

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


dpg.bind_theme(global_theme)
dpg.bind_font(global_font)

main()

check_conditions_thread = Thread(target=check_conditions_loop, daemon=True)
check_conditions_thread.start()

dpg.set_primary_window(WINDOW_ID, True)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
