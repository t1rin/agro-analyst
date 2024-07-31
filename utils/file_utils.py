import json, os


def _check_file_structure() -> None:
    paths = ["./data", "./data/images", "./data/results"]
    for path in paths:
        if not os.path.isdir(path):
            os.mkdir(path)
    file_name = "./data/images/images.json"
    text = "{}"
    if not os.path.isfile(file_name):
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(text)

def file_exists(file: str) -> bool:
    _check_file_structure()
    return os.path.exists(file)

def file_read(src: str) -> str:
    _check_file_structure()
    with open(src, "r", encoding="utf-8") as file:
        return file.read()

def file_write(file: str, text: str) -> None:
    _check_file_structure()
    with open(file, "w", encoding="utf-8") as file:
        file.write(text)

def json_read(src: str) -> dict:
    _check_file_structure()
    code = file_read(src)
    return json.loads(code)

def json_write(file: str, data: dict) -> None:
    _check_file_structure()
    json.dump(data, file, indent=4)
