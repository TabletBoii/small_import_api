import sys
import os

from fastapi import HTTPException, Security

from utils.constants import API_KEY, API_KEY_HEADER, API_KEY_QUERY
from datetime import datetime

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


async def get_api_key(api_key_header: str = Security(API_KEY_HEADER),
                      api_key_query: str = Security(API_KEY_QUERY)) -> str:
    if api_key_header == API_KEY:
        return api_key_header
    elif api_key_query == API_KEY:
        return api_key_query
    else:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid or missing API Key",
        )


def convert_iso_string_to_datetime(iso_string: str) -> datetime:
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    return dt
