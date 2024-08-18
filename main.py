import asyncio
import dearpygui.dearpygui as dpg

import threading
import webbrowser
import time

import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s][%(asctime)s] - %(name)s - %(message)s',
                    datefmt='%H:%M:%S')

logging.getLogger("asyncio").setLevel(logging.ERROR)

from asyncio import AbstractEventLoop

dpg.create_context()

from config import *
from templates import *
from identifiers import *
from theme_settings import *
from utils import *

from dpg_wrapper import DpgWrapper

if ENABLE_SEGMENTATION:
    from analyzer.segmentation import segmentation
if ENABLE_NEUROANALYSIS:
    from analyzer.classification import classification


logger = logging.getLogger(__name__)

results_and_items = {}
load_textures_tasks = []

scale = 1

_enabled_fullscreen = False

async def check_loop() -> None:
    interval = 1 / UPDATING_RATE
    while True:
        await check_images_dir()
        await check_results_dir()
        await asyncio.sleep(interval)

async def check_images_dir() -> None:
    # load .json
    images_json_file = "./data/images/images.json"
    data_images = await asyncio.to_thread(json_read, images_json_file)

    # show image
    list_images = await asyncio.to_thread(list_files, "./data/images")
    def get_time(name: str) -> list:
        if "_time_" in name:
            start = name.find("_time_") + 6
            end = name.find("_", start)
            return [int(name[start:end])]
        else:
            return []
        
    list_images = sorted(list_images, key=get_time)
    for image in list_images:
        img_exists = await asyncio.to_thread(image_exists, image)
        if not img_exists:
            continue
        await show_image(image)
        if path_basename(image).startswith('_'):
            await asyncio.to_thread(file_delete, image)

    # image analysis
    if not data_images:
        if data_images is None:
            await asyncio.to_thread(json_write, images_json_file)
        return
    
    await asyncio.to_thread(json_write, images_json_file)

    for name, data in data_images.items():
        img_name = f"./data/images/{name}"

        img_exists = await asyncio.to_thread(image_exists, img_name)
        if not img_exists:
            logger.warning(f"Не найден снимок {img_name}")
            continue
        
        image = await asyncio.to_thread(load_image, img_name)
        await asyncio.to_thread(file_delete, img_name)
        
        asyncio.create_task(image_analysis(image, img_name, data))

async def show_image(img_name: str) -> None:
    global dpg_wrapper, id_generator

    img_exists = await asyncio.to_thread(image_exists, img_name)
    if not img_exists:
        return
    img_basename = path_basename(img_name)
    if img_basename.startswith('_'):
        base_name = ".".join(img_basename.split(".")[:-1])
        keys = base_name.split("_")[1::2]
        values = base_name.split("_")[2::2]
        data = dict(zip(keys, values))
    else: data = None

    image = await asyncio.to_thread(load_image, img_name)
    height, width = image.shape[:2]

    if dpg.does_item_exist(TEXTURE_SHOW_IMAGE):
        dpg.delete_item(TEXTURE_SHOW_IMAGE)

    texture_data = await asyncio.to_thread(convert_to_texture_data, image.copy())
    create_texture(width, height, texture_data, tag=TEXTURE_SHOW_IMAGE)

    dpg_wrapper.configure_item(
        item=PREVIEW_IMAGE1_ID, 
        texture_tag=TEXTURE_SHOW_IMAGE, 
        bounds_min=[0, 0], 
        bounds_max=[width, height]
    )

    dpg_wrapper.configure_item(PREVIEW_IMAGE2_ID, texture_tag=TEXTURE_SHOW_IMAGE)

    if data: dpg.set_value(PREVIEW_TEXT_SENSORS_ID, format_text(TEXT_SENSORS_PANEL, data))

async def image_analysis(image: MatLike, img_name: str, data: dict) -> None:
    global dpg_wrapper
    
    logger.info(f"Найден новый снимок для анализа {img_name}")

    dpg_wrapper.configure_item(ANALYSIS_INDICATOR_ID, show=True)
    dpg_wrapper.configure_item(BUTTON_SHOW_RESULT, show=False)

    logger.info(f"Снимок {img_name} в обработке")

    if ENABLE_SEGMENTATION:
        stamp = time.time()
        segments = await asyncio.to_thread(segmentation, image)
        logger.debug(f"Время сегментирования {(time.time() - stamp):.2f} сек")
    else:
        segments = []
        logger.debug("Сегментация отключена")

    if ENABLE_NEUROANALYSIS:
        stamp = time.time()
        classification_ = await asyncio.to_thread(classification, image)
        logger.debug(f"Время классификации {(time.time() - stamp):.2f} сек")
    else:
        classification_ = "Классификация отключена"
        logger.debug("Классификация отключена")

    analysis_data = {
        "classification": classification_,
    }

    # for i in range(len(segments)):
    #     analysis_data[i] = ...

    path = await save_results(segments, data, analysis_data, image)

    logger.info(f"Обработан и сохранён {path}")

    dpg_wrapper.configure_item(ANALYSIS_INDICATOR_ID, show=False)

    texture = TEXTURE_SHOW_RESULT
    dpg_wrapper.delete_item(texture) # FIXME

    size = DEFAULT_SIZE_BUTTON
    square = await asyncio.to_thread(make_square_image, image, size)
    texture_data = await asyncio.to_thread(convert_to_texture_data, square)
    create_texture(size, size, texture_data, tag=texture)
    dpg_wrapper.configure_item(
        item=BUTTON_SHOW_RESULT,
        texture_tag=texture,
        user_data=path,
        show=True,
    )

async def save_results(segments: list, data: dict, analysis_data: dict, image: MatLike) -> int:
    i = 0
    while not i or dir_exists(path):
        time_ = int(time.time()) + i
        path = f"./data/results/{time_}"
        i += 1

    await asyncio.to_thread(makedir, path)

    save_tasks = [
        asyncio.to_thread(image_record, join_path(path, "source.jpeg"), image),
        asyncio.to_thread(json_write, join_path(path, "source_data.json"), data),
        asyncio.to_thread(json_write, join_path(path, "analysis_data.json"), analysis_data),
    ]

    for i, segment in enumerate(segments):
        save_tasks.append(asyncio.to_thread(image_record, join_path(path, f"{i}.jpeg"), segment))

    await asyncio.gather(*save_tasks)

    return path

async def check_results_dir() -> None:
    global results_and_items
    list_res = await asyncio.to_thread(list_dirs, "./data/results")
    new_results = list(set(list_res) - set(results_and_items.keys()))

    if not new_results:
        return

    dpg.set_value(COUNTER_TAB_TEXT_ID, f"Снимков: {len(list_res)}")

    await load_results_textures(list_res)

async def get_textures_pos(quantity: int, size: int, min_padding: int) -> list[tuple] | None:
    width, _ = dpg.get_item_rect_size(SELECTION_CHILD_ID)

    if not width:
        return

    columns = width // (size + min_padding)
    columns = max(columns, 1)

    rows = quantity // columns + (quantity % columns != 0)

    if columns * rows < quantity:
        logger.error("quantity больше возможного")

    padding = (width - columns * size) / (columns + 1)

    pos_textures = []

    i = 0
    for row in range(rows):
        for column in range(columns):
            if i >= quantity:
                break
            pos_textures.append((column*size + (column + 1)*padding,
                                 row*size + (row + 1)*padding))
            i += 1

    return pos_textures

async def delete_results_textures() -> None:
    global load_textures_tasks
    for task in load_textures_tasks:
        task.cancel()
    load_textures_tasks.clear()

    dpg_wrapper.delete_item(SELECTION_CHILD_ID, children_only=True)

    global results_and_items, id_generator
    for result, items in results_and_items.items():
        image_button_id, texture_id = items
        dpg_wrapper.delete_item(texture_id)
        id_generator.release_id(image_button_id, texture_id)
        results_and_items[result] = (None, None)

async def load_result_texture(result: str, size: int, btn_padding: int, position: tuple) -> None:
    names = ["source.jpeg", "analysis_data.json"]
    for name in names:
        file_name = join_path(result, name)
        if not file_exists(file_name):
            logger.error(f"Файл {name} не найден в папке {result}")
            return
    
    global results_and_items, id_generator

    image = await asyncio.to_thread(load_image, join_path(result, "source.jpeg"))
    analysis_data = await asyncio.to_thread(json_read, join_path(result, "analysis_data.json"))
    analysis_data = NoneDict(analysis_data)

    square = await asyncio.to_thread(make_square_image, image, size)
    texture_data = await asyncio.to_thread(convert_to_texture_data, square)
    texture_id = create_texture(size, size, texture_data)
    id_generator.add_active_id(texture_id)

    indicator_id = results_and_items[result][1]

    image_button_id = id_generator.generate_id()

    results_and_items[result] = (image_button_id, texture_id)

    dpg_wrapper.add_item(
        item_type_="image_button",
        parent=SELECTION_CHILD_ID,
        texture_tag=texture_id,
        callback=show_result,
        user_data=result,
        frame_padding=btn_padding,
        tag=image_button_id,
        pos=position,
    )

    status = analysis_data["classification"]

    tooltip_id = id_generator.generate_id()
    dpg_wrapper.add_item(item_type_="tooltip", parent=image_button_id, tag=tooltip_id)
    dpg_wrapper.dpg_command(dpg.bind_item_font, item=tooltip_id, font=tooltip_font)
    dpg_wrapper.add_item(item_type_="text", parent=tooltip_id, default_value=status)

    dpg_wrapper.delete_item(indicator_id)

async def load_results_textures(results: list[str]) -> None:
    await delete_results_textures()

    results.sort()

    global scale, results_and_items, id_generator, load_textures_tasks

    btn_padding = PADDING_BUTTON_SELECTION
    size_btn = int(DEFAULT_SIZE_BUTTON * scale)
    size = int(size_btn + btn_padding*2)
    min_padding = MIN_PADDING_SELECTION

    positions = await get_textures_pos(len(results), size, min_padding)
    if not positions:
        results_and_items.clear()
        return
    for i, position in enumerate(positions):
        id = id_generator.generate_id()
        result = results[i]
        results_and_items[result] = (None, id)
        dpg_wrapper.add_item(
            item_type_="loading_indicator",
            parent=SELECTION_CHILD_ID,
            pos=position,
            radius=3.5*scale,
            style=1,
            tag=id,
        )

        load_textures_tasks.append(
            asyncio.create_task(load_result_texture(result, size_btn, btn_padding, position))
        )

    try: await asyncio.gather(*load_textures_tasks)
    except asyncio.CancelledError: pass

async def update_list_results() -> None:
    global load_textures_tasks

    def tasks_is_done(tasks) -> bool:
        return all(task.done() for task in tasks)

    if not tasks_is_done(load_textures_tasks):
        time_stamp = time.time()
        while time.time() - time_stamp < 3:
            await asyncio.sleep(0.1)
            if tasks_is_done(load_textures_tasks):
                break
        else:
            return

    global results_and_items

    if not results_and_items:
        return

    buttons, _ = zip(*results_and_items.values())

    btn_padding = PADDING_BUTTON_SELECTION
    size_btn = int(DEFAULT_SIZE_BUTTON * scale)
    size = int(size_btn + btn_padding*2)
    min_padding = MIN_PADDING_SELECTION

    positions = await get_textures_pos(len(buttons), size, min_padding)
                  
    for i, position in enumerate(positions):
        dpg_wrapper.configure_item(buttons[i], pos=position)

def change_tab_callback(_, __, widget_id: int) -> None:
    asyncio.run(change_tab(widget_id))

def fullscreen_callback(sender: int, __) -> None:
    global _enabled_fullscreen
    dpg.toggle_viewport_fullscreen()
    _enabled_fullscreen = not _enabled_fullscreen
    dpg.configure_item(PREVIEW_TEXT_TIME_ID, show=_enabled_fullscreen)
    logger.info(("Включен" if _enabled_fullscreen else "Выключен") + " полноэкранный режим")

def simple_preview_callback(_, __) -> None:
    simple_preview = dpg.get_value(SIMPLE_PREVIEW_MENU_ITEM_ID)
    dpg.configure_item(PREVIEW_IMAGE2_ID, show=(simple_preview))
    dpg.configure_item(PREVIEW_PLOT_ID, show=(not simple_preview))
    logger.info(
        "Выбран простой режим просмотра " if simple_preview
        else "Выбран стандартный режим просмотра"
    )

def scale_callback(_, __, action: str) -> None:
    scale_delta = {"--": -1, "-": -0.1, "+": +0.1, "++": +1}

    global scale
    scale += scale_delta[action]

    scale = min(scale, 10)
    scale = max(scale, 0.2)

    results = list_dirs("./data/results")

    dpg.set_value(SCALE_TEXT_ID, f"{scale:.1f}")

    asyncio.run(load_results_textures(results))

def run_func_debug() -> None:
    logger.debug("Отладочная функция запущена")
    # results = list_dirs("./data/results")
    # asyncio.run(load_results_textures(results))

def show_result(_, __, result_path: str) -> None:
    logger.debug(f"Путь к выбранному результату: {result_path}")

    name_source_data = join_path(result_path, "source_data.json")
    source_data = json_read(name_source_data)

    name_analysis_data = join_path(result_path, "analysis_data.json")
    analysis_data = json_read(name_analysis_data)

    dpg.set_value(
        VIEWER_TEXT_INFO_ID,
        format_text(TEXT_INFO_PANEL, source_data),
    )

    dpg.set_value(
        VIEWER_TEXT_STATUS_ID,
        format_text(TEXT_STATUS_PANEL, analysis_data)
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
    viewport_width = dpg.get_viewport_width()
    viewport_height = dpg.get_viewport_height()
    width, height = WIDTH_ABOUT_WINDOW, HEIGHT_ABOUT_WINDOW

    dpg.configure_item(item=ABOUT_WINDOW_ID, pos=((viewport_width - width) / 2, (viewport_height - height) / 2))

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

    results = await asyncio.to_thread(list_dirs, "./data/results")
    await load_results_textures(results)

    await update_menu_bar()

async def create_about_window() -> None:
    viewport_width = VIEWPORT_OPTIONS["width"]
    viewport_height = VIEWPORT_OPTIONS["height"]
    width, height = WIDTH_ABOUT_WINDOW, HEIGHT_ABOUT_WINDOW
    with dpg.window(tag=ABOUT_WINDOW_ID, width=width, height=height, show=False, pos=((viewport_width - width) / 2, (viewport_height - height) / 2), modal=True, no_title_bar=True, no_resize=True, no_move=True):
        dpg.add_text(TEXT_ABOUT_INFO, indent=6, wrap=0)
        dpg.bind_item_font(dpg.last_item(), about_font)
        width_btn, height_btn, padding = 80, 30, 20
        dpg.add_button(label="Close", width=width_btn, height=height_btn, pos=((width - width_btn - padding), (height - height_btn - padding)), callback=lambda: dpg.configure_item(ABOUT_WINDOW_ID, show=False))

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
            with dpg.group(parent=dpg.last_item(), horizontal=True):
                dpg.add_button(label="<<", callback=scale_callback, user_data="--")
                dpg.add_button(label="<", callback=scale_callback, user_data="-")
                dpg.add_text("1", tag=SCALE_TEXT_ID)
                dpg.add_button(label=">", callback=scale_callback, user_data="+")
                dpg.add_button(label=">>", callback=scale_callback, user_data="++")
        with dpg.menu(label=MENU_BAR["menus"]["help"]):
            dpg.bind_item_font(dpg.last_item(), menu_font)
            dpg.add_menu_item(label=MENU_BAR["help"]["about"], callback=lambda: dpg.configure_item(ABOUT_WINDOW_ID, show=True))
            dpg.add_menu_item(label=MENU_BAR["help"]["github"], callback=lambda: webbrowser.open("https://github.com/t1rin/agro-analyst"))

async def create_tab_bar() -> None:
    with dpg.child_window(autosize_x=True, show=SHOW_TAB_BAR, height=46): # HACK
        with dpg.group(horizontal=True):
            dpg.add_text(tag=PREVIEW_TEXT_TIME_ID, show=False)
            dpg.bind_item_font(dpg.last_item(), time_font)
            dpg.add_button(label=MENU_BAR["view"]["preview"], 
                callback=change_tab_callback, user_data=PREVIEW_TAB_ID,
                tag=PREVIEW_TAB_BUTTON_ID)
            dpg.add_button(label=MENU_BAR["view"]["selection"], 
                callback=change_tab_callback, user_data=SELECTION_TAB_ID,
                tag=SELECTION_TAB_BUTTON_ID)
            dpg.add_button(label=MENU_BAR["view"]["viewer"], 
                callback=change_tab_callback, user_data=VIEWER_TAB_ID,
                tag=VIEWER_TAB_BUTTON_ID)
            dpg.add_text(tag=COUNTER_TAB_TEXT_ID)
            if logger.getEffectiveLevel() == logging.DEBUG:
                dpg.add_button(label="RUN FUNC", callback=run_func_debug)
                dpg.add_text(tag=FPS_DEBUG_TEXT_ID)
                dpg.add_text(tag=IDS_DEBUG_TEXT_ID)

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
                                dpg.add_text(format_text(TEXT_SENSORS_PANEL), 
                                    tag=PREVIEW_TEXT_SENSORS_ID, indent=8, wrap=0)
                            with dpg.collapsing_header(label="Анализ (последний)", default_open=True):
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
                                dpg.add_text(format_text(TEXT_STATUS_PANEL), 
                                    tag=VIEWER_TEXT_STATUS_ID, indent=8, wrap=0)
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

    await create_about_window()

    await change_tab(PREVIEW_TAB_ID)

    logger.debug(f"Initialization completed. ({(time.time() - time_stamp):.5f})")

def run_async_tasks(loop: AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_until_complete(check_loop())


if __name__ == "__main__":
    logger.info("Initialization...")

    id_generator = IdGenerator()

    dpg_wrapper = DpgWrapper()

    dpg.create_viewport(**VIEWPORT_OPTIONS)

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
        ### Check active id
        active_identifiers = list(id_generator.active_identifiers)
        for identifier in active_identifiers:
            if not dpg.does_item_exist(identifier):
                id_generator.release_id(identifier)
        ### Update time label
        if _enabled_fullscreen:
            seconds = int(time.time())
            strtime = seconds_to_str(seconds, TIME_FORMAT)
            dpg.set_value(PREVIEW_TEXT_TIME_ID, strtime)
        ### Show debug info
        if logger.getEffectiveLevel() == logging.DEBUG:
            ### FPS
            normal_fps = 60
            fps = dpg.get_frame_rate()
            share = min(fps / normal_fps, 1)
            dpg.set_value(item=FPS_DEBUG_TEXT_ID, value=f"FPS: {fps:.2f}")
            dpg.configure_item(item=FPS_DEBUG_TEXT_ID,
                color=(255-255*share, 255*share, 0, 255))
            ### Active ID
            quantity_active_ids = len(active_identifiers)
            quantity_free_ids = len(id_generator.free_identifiers)
            dpg.set_value(
                item=IDS_DEBUG_TEXT_ID, 
                value=f"All IDs: {quantity_active_ids + quantity_free_ids}; Active IDs: {quantity_active_ids}; Free IDs: {quantity_free_ids}")
        ### Updating DearPyGui
        dpg_wrapper.update_dpg()
        dpg.render_dearpygui_frame()

dpg.destroy_context()
