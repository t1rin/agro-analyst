import json, os


def file_exists(file: str) -> bool:
    return os.path.exists(file)

def file_read(src: str) -> str:
    with open(src, "r", encoding="utf-8") as file:
        return file.read()

def file_write(file: str, text: str) -> None:
    with open(file, "w", encoding="utf-8") as file:
        file.write(text)

def json_read(src: str) -> dict:
    code = file_read(src)
    return json.loads(code)

def json_write(file: str, data: dict) -> None:
    json.dump(data, file, indent=4)
