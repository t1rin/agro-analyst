import dearpygui.dearpygui as dpg

global_font_path = "./assets/fonts/DeleddaOpen.ttf"
menu_font_path = "./assets/fonts/DeleddaOpen.ttf"

with dpg.font_registry():
    with dpg.font(global_font_path, size=16) as global_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

    with dpg.font(menu_font_path, size=14) as menu_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
