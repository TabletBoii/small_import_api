import sys
import os

import numpy as np
from fastapi import HTTPException, Security
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials
from pandas import DataFrame

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


def process_result_data(fetched_data: DataFrame, field_names: dict = None):
    if field_names is not None:
        fetched_data = fetched_data.loc[:, list(field_names.keys())]
        fetched_data = fetched_data.rename(columns=field_names)
    fetched_data = fetched_data.replace(np.nan, None)
    fetched_data = fetched_data.to_dict(orient='records')
    resulted_data = jsonable_encoder(fetched_data)
    return resulted_data


def format_dates_for_functions(dates_raw):
    return [
        datetime.strptime(d, '%Y-%m-%d')
        for d in dates_raw if d.strip()
    ]


def find_min_date(dates_raw):

    return min(format_dates_for_functions(dates_raw)).strftime('%Y-%m-%d')


def find_max_date(dates_raw):

    return max(format_dates_for_functions(dates_raw)).strftime('%Y-%m-%d')
