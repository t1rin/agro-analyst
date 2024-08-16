import dearpygui.dearpygui as dpg

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 6, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 10, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 8, 8, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 14, category=dpg.mvThemeCat_Core)

        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (16, 16, 16), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (50, 50, 55), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (28, 28, 28), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (28, 28, 28), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (28, 28, 28), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (225, 225, 225), category=dpg.mvThemeCat_Core)

    with dpg.theme_component(dpg.mvTable):
        dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 2, 0, category=dpg.mvThemeCat_Core)

    with dpg.theme_component(dpg.mvPlot):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (28, 28, 28), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvPlotCol_Selection, (0, 120, 215), category=dpg.mvThemeCat_Plots)

with dpg.theme() as active_tab_button_theme:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (29,151,236,103), category=dpg.mvThemeCat_Core) 

with dpg.theme() as selection_theme:
    with dpg.theme_component(dpg.mvChildWindow):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (16, 16, 16), category=dpg.mvThemeCat_Core)
