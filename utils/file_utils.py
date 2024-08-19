import json, os, logging

from json import JSONDecodeError

logger = logging.getLogger(__name__)


def _check_file_structure() -> None:
    paths = ["./data", "./data/images", "./data/results"]
    for path in paths:
        if not os.path.isdir(path):
            os.mkdir(path)
    file_name = "./data/images/images.json"
    if not os.path.isfile(file_name):
        with open(file_name, "w", encoding="utf-8") as file:
            file.write("{}")

def file_exists(file: str) -> bool:
    _check_file_structure()
    return os.path.isfile(file)

def file_read(src: str) -> str | None:
    _check_file_structure()
    if file_exists(src):
        with open(src, "r", encoding="utf-8") as file:
            return file.read()
    else:
        logger.error(f"Ошибка чтения. Файла {src} не существует")

def file_write(file: str, text: str) -> None:
    _check_file_structure()
    with open(file, "w", encoding="utf-8") as file:
        file.write(text)

def file_delete(file: str) -> None:
    if file_exists(file):
        os.remove(file)

def path_basename(abs_path: str) -> None:
    return os.path.basename(abs_path)

def dir_exists(dir: str) -> bool:
    _check_file_structure()
    return os.path.isdir(dir)

def json_read(src: str) -> dict:
    _check_file_structure()
    code = file_read(src)
    try:
        return json.loads(code)
    except JSONDecodeError:
        logger.error("Файл .JSON имеет некорректную структуру")

def json_write(file: str, data: dict = {}) -> None:
    _check_file_structure()
    code = json.dumps(data, indent=4)
    file_write(file, code)

def json_update(file: str, data: dict) -> None:
    _check_file_structure()
    old_code = file_read(file)
    try: old_data = json.loads(old_code)
    except: old_data = {}
    old_data.update(data)
    json_write(file, old_data)

def makedir(path: str) -> None:
    try:
        os.makedirs(path)
    except FileExistsError:
        logger.error(f"Директория {path} уже существует")

def join_path(path: str, *names: str) -> str:
    return os.path.join(path, *names)

def parent_dir(path: str) -> str:
    return os.path.dirname(os.path.abspath(path))
