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

class NoneDict(dict):
    def __missing__(self, key) -> None:
        return None

def format_text(template: str, values: dict | NoneDict = {}) -> str:
    if type(values) != NoneDict:
        values = NoneDict(values)
    return template.format_map(values)
