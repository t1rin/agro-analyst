import dearpygui.dearpygui as dpg

global_font_path = "./assets/fonts/DeleddaOpen.ttf"
menu_font_path = "./assets/fonts/DeleddaOpen.ttf"
about_font_path = "./assets/fonts/DeleddaOpen.ttf"
tooltip_font_path = "./assets/fonts/DeleddaOpen.ttf"
time_font_path = "./assets/fonts/DeleddaOpen.ttf"

with dpg.font_registry():
    with dpg.font(global_font_path, size=16) as global_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

    with dpg.font(menu_font_path, size=14) as menu_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

    with dpg.font(about_font_path, size=18) as about_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

    with dpg.font(tooltip_font_path, size=18) as tooltip_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

    with dpg.font(time_font_path, size=18) as time_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
