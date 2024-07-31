import os

from utils.file_utils import _check_file_structure


def list_files(path: str) -> list[str]:
    _check_file_structure()
    names = os.listdir(path)
    files = []
    for name in names:
        path_and_name = os.path.join(path, name)
        if os.path.isfile(path_and_name):
            files.append(name)
    return files
