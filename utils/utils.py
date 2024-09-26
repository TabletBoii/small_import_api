import os
import sys


def get_data(key: str) -> any:
    return os.environ.get(key)


def is_file_open(file_path):
    try:
        with open(file_path, 'a'):
            return False
    except IOError:
        return True


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
