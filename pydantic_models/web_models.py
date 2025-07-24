from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Direction(BaseModel):
    inc: Optional[int] = 0
    airline_name: Optional[str]
    country_of_departure: Optional[str]
    country_of_arrival: Optional[str]
    town_of_departure: Optional[str]
    town_of_arrival: Optional[str]
    town_of_departure_alias: str
    town_of_arrival_alias: str
    airline_alias: Optional[str]
    status: str
    flight_alias: Optional[str]


class DownloadItem(BaseModel):
    id: int
    resource_name: str
    created_date: datetime
    in_process: bool
    has_error: bool
    is_downloaded: bool
    params: str
    error_msg: str | None
