import os


def list_files(path: str) -> list[str]:
    names = os.listdir(path)
    files = []
    for name in names:
        path_and_name = os.path.join(path, name)
        if os.path.isfile(path_and_name):
            files.append(name)
    return files
