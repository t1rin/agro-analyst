import asyncio
import dearpygui.dearpygui as dpg

import threading
import time

from asyncio import AbstractEventLoop

import logging

logging.basicConfig(level=logging.DEBUG,
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

from dpg_wrapper import DpgWrapper


analysis_results = {}
scale = 1

free_identifiers = []

async def check_loop() -> None:
    interval = 1 / UPDATING_RATE
    while True:
        await check_images_dir()
        await check_results_dir()
        await asyncio.sleep(interval)

async def check_images_dir() -> None:
    images_json_file = "./data/images/images.json"
    data_images = await asyncio.to_thread(json_read, images_json_file)

    if not data_images:
        if data_images is None:
            await asyncio.to_thread(json_write, images_json_file)
        return
    
    await asyncio.to_thread(json_write, images_json_file)

    task = []
    for name, data in data_images.items():
        img_name = f"./data/images/{name}"
        task.append(asyncio.create_task(image_analysis(img_name, data)))
    asyncio.gather(*task)

async def image_analysis(img_name: str, data: dict) -> None:
    img_exists = await asyncio.to_thread(file_exists, img_name)
    if not img_exists:
        stamp = time.time()
        while time.time() - stamp < 3:
            await asyncio.sleep(0.1)
        if not (await asyncio.to_thread(file_exists, img_name)):
            logger.warning(f"Не найден снимок {img_name}")
            return
    
    logger.info(f"Найден новый снимок {img_name}")

    image = await asyncio.to_thread(load_image, img_name)
    await asyncio.to_thread(file_delete, img_name)

    height, width = image.shape[:2]
    texture_data = await asyncio.to_thread(convert_to_texture_data, image.copy())
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

    stamp = time.time()
    segments = await asyncio.to_thread(segmentation, image)
    logger.debug(f"Время сегментирования {(time.time() - stamp):.2f} сек")

    analysis_data = {} # TODO

    # for i in range(len(segments)):
    #     analysis_data[i] = ...

    await save_result(segments, data, analysis_data, image)

async def save_result(segments: list, data: dict, analysis_data: dict, image) -> None:
    path = f"./data/results/{int(time.time())}"

    await asyncio.to_thread(makedir, path)

    save_tasks = [
        asyncio.to_thread(image_record, join_path(path, "source.jpeg"), image),
        asyncio.to_thread(json_write, join_path(path, "source_data.json"), data),
        asyncio.to_thread(json_write, join_path(path, "analysis_data.json"), analysis_data),
    ]

    for i, segment in enumerate(segments):
        save_tasks.append(asyncio.to_thread(image_record, join_path(path, f"{i}.jpeg"), segment))

    await asyncio.gather(*save_tasks)    

    logger.info(f"Обработан и сохранён {path}")

    dpg.hide_item(ANALYSIS_INDICATOR_ID)

    texture = TEXTURE_SHOW_RESULT
    dpg.delete_item(texture)

    size = DEFAULT_SIZE_BUTTON
    square = await asyncio.to_thread(make_square_image, image, size)
    texture_data = await asyncio.to_thread(convert_to_texture_data, square)
    create_texture(size, size, texture_data, tag=texture)
    await asyncio.to_thread(dpg.configure_item,
        item=BUTTON_SHOW_RESULT,
        texture_tag=texture,
        user_data=path,
        show=True,
    )

async def check_results_dir() -> None:
    global analysis_results
    list_res = await asyncio.to_thread(list_dirs, "./data/results")
    new_results = list(set(list_res) - set(analysis_results.keys()))

    if not new_results:
        return

    await delete_results_textures()
    await load_results_textures(list_res)

async def load_result_texture(result: str, size: int) -> None:
    global free_identifiers, analysis_results
    image = await asyncio.to_thread(load_image, join_path(result, "source.jpeg"))
    square = await asyncio.to_thread(make_square_image, image, size)
    texture_data = await asyncio.to_thread(convert_to_texture_data, square)
    if free_identifiers:
        texture = free_identifiers.pop()
    else:
        texture = dpg.generate_uuid()
    create_texture(size, size, texture_data, tag=texture)
    analysis_results[result] = texture

async def load_results_textures(results: list[str]) -> None:
    global scale
    size = int(DEFAULT_SIZE_BUTTON * scale)

    load_tasks = [load_result_texture(result, size) 
                  for result in results]
    
    await asyncio.gather(*load_tasks)

    await update_list_results()

async def delete_results_textures() -> None:
    dpg.delete_item(SELECTION_CHILD_ID, children_only=True)

    global analysis_results, free_identifiers
    textures = analysis_results.values()
    for texture in textures:
        dpg.delete_item(texture)
        free_identifiers.append(texture)
    analysis_results.clear()

async def update_list_results() -> None:
    dpg.delete_item(SELECTION_CHILD_ID, children_only=True)
    
    global analysis_results, scale
    quantity = len(analysis_results)
    if not quantity:
        return
    sorted_results = sorted(analysis_results.items())
    paths, textures = zip(*sorted_results)

    results = [] # TODO
    for path in paths:
        from random import randint 
        good = randint(0, 4)
        if good:
            results.append(("Никаких отклонений от нормы не найдено", good))
        else:
            results.append(("Найдены отклонения от нормы!", good)) # TODO

    width, _ = dpg.get_item_rect_size(SELECTION_CHILD_ID)
    btn_padding = PADDING_BUTTON_SELECTION
    size_btn = int(DEFAULT_SIZE_BUTTON * scale + btn_padding * 2)
    min_padding = MIN_PADDING_SELECTION

    columns = width // (size_btn + min_padding)
    columns = max(columns, 1)

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
                pos=(column*size_btn + (column + 1)*padding,
                     row*size_btn + (row + 1)*padding))
            with dpg.tooltip(dpg.last_item()):
                status, good = results[i]
                dpg.add_text(status, color=(0, 255, 0) if good else (255, 0, 0))
            i += 1  

def change_tab_callback(_, __, widget_id: int) -> None:
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
    asyncio.run(delete_results_textures())
    asyncio.run(load_results_textures(results))

def show_result(_, __, result_path: str) -> None:
    logger.debug(f"Путь к выбранному результату: {result_path}")
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

    change_tab_callback(None, None, VIEWER_TAB_ID)

def resize_callback(_, __) -> None:
    asyncio.run(update_list_results())

def close_all_on_exit() -> None:
    global event_loop
    event_loop.stop()

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

    await delete_results_textures()

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
            dpg.add_text(tag=FPS_TEXT_LABEL_ID)

async def init_interface() -> None:
    time_stamp = time.time()
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
                                        callback=show_result,
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

    logger.debug(f"Initialization completed. ({(time.time() - time_stamp):.5f})")

def run_async_tasks(loop: AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_until_complete(check_loop())


if __name__ == "__main__":
    logger.info("Initialization...")

    dpg_wrapper = DpgWrapper()

    dpg.create_viewport(**VIEWPORT_OPTIONS)
    dpg.set_viewport_max_height(MAX_HEIGHT)
    dpg.set_viewport_max_width(MAX_WIDTH)
    dpg.set_viewport_min_height(MIN_HEIGHT)
    dpg.set_viewport_min_width(MIN_WIDTH)

    dpg.bind_theme(global_theme)
    dpg.bind_font(global_font)

    asyncio.run(init_interface())

    dpg.set_viewport_resize_callback(resize_callback)
    dpg.set_exit_callback(close_all_on_exit)

    dpg.set_primary_window(WINDOW_ID, True)

    dpg.setup_dearpygui()
    dpg.show_viewport()

    event_loop = asyncio.new_event_loop()
    threading.Thread(target=run_async_tasks, args=(event_loop,), daemon=True).start()

    while dpg.is_dearpygui_running():
        if logger.getEffectiveLevel() == logging.DEBUG:
            normal_fps = 60
            fps = dpg.get_frame_rate()
            share = min(fps / normal_fps, 1)
            dpg.set_value(item=FPS_TEXT_LABEL_ID, value=f"FPS: {fps:.2f}")
            dpg.configure_item(item=FPS_TEXT_LABEL_ID,
                color=(255-255*share, 255*share, 0, 255)) 
        dpg_wrapper.update_dpg()
        dpg.render_dearpygui_frame()

dpg.destroy_context()
