import os

from utils.file_utils import (
    _check_file_structure,
    join_path,
)


def listdir(path: str) -> list[str]:
    names = os.listdir(path)
    return [join_path(path, name) 
            for name in names]

def list_files(path: str) -> list[str]:
    _check_file_structure()
    names = listdir(path)
    return [name for name in names if os.isfile(name)]

def list_dirs(path: str) -> list[str]:
    _check_file_structure()
    names = listdir(path)
    return [name for name in names if os.isdir(name)]
