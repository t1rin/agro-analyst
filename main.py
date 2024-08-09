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

analysis_results = {} # key - result path name; # value - texture id for button
scale = 1 # TODO
                     
def check_conditions_loop() -> None:
    pause = 1 / UPDATING_RATE
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
    texture_data = convert_to_texture_data(image.copy())

    texture = create_texture(width, height, texture_data)

    dpg.configure_item(
        item=PREVIEW_IMAGE1_ID, 
        texture_tag=texture, 
        bounds_min=[0, 0], 
        bounds_max=[width, height]
    )

    dpg.configure_item(PREVIEW_IMAGE2_ID, texture_tag=texture)

    data = NoneDict(data)
    time_ = data["time"]
    if time_:
        data["time"] = seconds_to_str(time_)
    data["width"] = width
    data["height"] = height

    dpg.set_value(
        PREVIEW_TEXT_INFO_ID,
        format_text(TEXT_INFO_PANEL, data),
    )

    dpg.show_item(ANALYSIS_INDICATOR_ID)
    dpg.hide_item(BUTTON_SHOW_RESULT)

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

    dpg.hide_item(ANALYSIS_INDICATOR_ID)

    size = 60 # TODO
    square = make_square_image(image, size)
    texture_data = convert_to_texture_data(square)
    texture = create_texture(size, size, texture_data)
    dpg.configure_item(
        item=BUTTON_SHOW_RESULT,
        texture_tag=texture,
        user_data=path,
        show=True,
    )

def check_results_dir() -> None:
    global analysis_results
    list_res = list_dirs("./data/results")
    new_results = list(set(list_res) - set(analysis_results.keys()))

    if not new_results: 
        return
    
    for new_result in new_results:
        image = load_image(join_path(new_result, "source.jpeg"))
        square = make_square_image(image, DEFAULT_SIZE_BUTTON)
        texture_data = convert_to_texture_data(square)
        texture = create_texture(
            DEFAULT_SIZE_BUTTON,
            DEFAULT_SIZE_BUTTON,
            texture_data,
        )
        analysis_results[new_result] = texture

    update_list_results()

def update_list_results() -> None:
    dpg.delete_item(SELECTION_CHILD_ID, children_only=True)

    global analysis_results
    quantity = len(analysis_results)
    paths = list(analysis_results.keys())
    textures = list(analysis_results.values())

    width, _ = dpg.get_item_rect_size(SELECTION_CHILD_ID)
    if not width: return
    size_btn = DEFAULT_SIZE_BUTTON # * scale # TODO
    min_padding = MIN_PADDING_SELECTION
    btn_padding = PADDING_BUTTON_SELECTION

    columns = width // (size_btn + min_padding)
    rows = quantity // columns + (quantity % columns != 0)

    padding = (width - columns * size_btn) / (columns + 1)

    i = 0
    for row in range(rows):
        for column in range(columns):
            if i >= quantity:
                break
            dpg.add_image_button(
                parent=SELECTION_CHILD_ID,
                texture_tag=textures[i],
                callback=show_result,
                user_data=paths[i],
                frame_padding=btn_padding,
                pos=(column*(size_btn+btn_padding*2) + (column + 1)*padding,
                     row*(size_btn+btn_padding*2) + (row + 1)*padding)
            )
            i += 1
    

def simple_preview_callback(_, __) -> None:
    simple_preview = dpg.get_value(SIMPLE_PREVIEW_ITEM_ID)
    dpg.configure_item(PREVIEW_IMAGE2_ID, show=(simple_preview))
    dpg.configure_item(PREVIEW_PLOT_ID, show=(not simple_preview))
    logger.info(
        "Выбран простой режим просмотра " if simple_preview
        else "Выбран стандартный режим просмотра"
    )

def show_result(_, __, result_path: str) -> None:
    name_source_data = join_path(result_path, "source_data.json")
    source_data = json_read(name_source_data)

    dpg.set_value(
        VIEWER_TEXT_INFO_ID,
        format_text(TEXT_INFO_PANEL, source_data),
    )

    name_source_img = join_path(result_path, "source.jpeg")
    source_image = load_image(name_source_img)

    height, width = source_image.shape[:2]

    texture_data = convert_to_texture_data(source_image.copy())
    texture = create_texture(width, height, texture_data)    

    dpg.configure_item(
        item=VIEWER_IMAGE_ID, 
        texture_tag=texture, 
        bounds_min=[0, 0], 
        bounds_max=[width, height]
    )

    change_tab(_, __, VIEWER_TAB_ID)

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
    
    dpg.configure_item(
        item=SIMPLE_PREVIEW_ITEM_ID,
        show=main_tab_is_shown
    )

def change_tab(_, __, widget_id: int) -> None:
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

    update_menu_bar()
    update_list_results()

def create_tab_bar() -> None:
    with dpg.child_window(autosize_x=True, height=46): # HACK
        with dpg.group(horizontal=True):
            dpg.add_button(label=MENU_BAR["view"]["preview"], 
                callback=change_tab, user_data=PREVIEW_TAB_ID,
                tag=PREVIEW_TAB_BUTTON_ID)
            dpg.add_button(label=MENU_BAR["view"]["selection"], 
                callback=change_tab, user_data=SELECTION_TAB_ID,
                tag=SELECTION_TAB_BUTTON_ID)
            dpg.add_button(label=MENU_BAR["view"]["viewer"], 
                callback=change_tab, user_data=VIEWER_TAB_ID,
                tag=VIEWER_TAB_BUTTON_ID)
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
                                            no_menus=True, show=(not DEFAULT_SIMPLE_PREVIEW), tag=PREVIEW_PLOT_ID):
                                options = {"no_gridlines": True, "no_tick_marks": True, "no_tick_labels": True}
                                dpg.add_plot_axis(dpg.mvXAxis, **options) 
                                with dpg.plot_axis(dpg.mvYAxis, **options):
                                    dpg.add_image_series(
                                        create_texture(),
                                        [0, 0], [0, 0],
                                        tag=PREVIEW_IMAGE1_ID,
                                    )
                            dpg.add_image(
                                texture_tag=create_texture(),
                                tag=PREVIEW_IMAGE2_ID,
                                show=DEFAULT_SIMPLE_PREVIEW
                            )
                        with dpg.child_window():
                            dpg.add_button(label="Домой", width=-1)
                            dpg.add_button(label="Пауза", width=-1)
                            dpg.add_spacer()
                            with dpg.collapsing_header(label="Данные", default_open=True):
                                dpg.add_text(format_text(TEXT_INFO_PANEL), 
                                    tag=PREVIEW_TEXT_INFO_ID, indent=8, wrap=0)
                            with dpg.collapsing_header(label="Анализ", default_open=True):
                                with dpg.group(horizontal=True):
                                    dpg.add_loading_indicator(tag=ANALYSIS_INDICATOR_ID, show=False)
                                    dpg.add_image_button(
                                        create_texture(),
                                        tag=BUTTON_SHOW_RESULT,
                                        callback=show_result,
                                        show=False,
                                    )
            with dpg.group(tag=SELECTION_TAB_ID, show=False):
                with dpg.child_window():
                    with dpg.child_window(tag=SELECTION_CHILD_ID):
                        pass
            with dpg.group(tag=VIEWER_TAB_ID, show=False):
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
        # tab_bar()


dpg.bind_theme(global_theme)
dpg.bind_font(global_font)

main()

dpg.set_viewport_resize_callback(update_list_results)

check_conditions_thread = Thread(target=check_conditions_loop, daemon=True)
check_conditions_thread.start()

dpg.set_primary_window(WINDOW_ID, True)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
