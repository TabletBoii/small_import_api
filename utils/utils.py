import sys
import os

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials

from utils.constants import API_KEY, API_KEY_HEADER, security
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


async def get_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    token = credentials.credentials
    if token == API_KEY:
        return token
    else:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid or missing API Key",
        )


def convert_iso_string_to_datetime(iso_string: str) -> datetime:
    date_str_clean = iso_string.split(" (")[0]

    dt = datetime.strptime(date_str_clean, "%a %b %d %Y %H:%M:%S GMT%z")
    return dt
