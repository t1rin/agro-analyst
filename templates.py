TEXT_ABOUT_INFO = (
    "Система для анализа состояния сельскохозяйственных полей\n"
    "\n"
    "Проект в разработке...\n"
    "\n"
    "\n"
    "\n"
    "https://github.com/t1rin/agro-analyst\n"
)

TEXT_SENSORS_PANEL = (
    "Глобальные (X, Y): ({x}, {y})\n"
    "\n"
    "Локальные X: {localx}\n"
    "\n"
    "Локальные Y: {localy}\n"
    "\n"
    "Локальные Z: {localz}\n"
)

TEXT_INFO_PANEL = (
    "Снимок сделан {time}\n"
    "\n"
    "Координаты снимка: {coords}\n"
    "\n"
    "Разрешение: {width}x{height}\n"
)

TEXT_DATA_PANEL = (
    " . . . "
)

TEXT_STATUS_PANEL = (
    "Классификация:\n"
    "\t{classification}\n"
)

class NoneDict(dict):
    def __missing__(self, key) -> None:
        return None

def format_text(template: str, values: dict | NoneDict = {}) -> str:
    if type(values) != NoneDict:
        values = NoneDict(values)
    return template.format_map(values)
