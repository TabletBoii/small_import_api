from typing import Dict, List, Optional, Tuple, Any

from fastapi import Depends, Form, Body
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import HTMLResponse

from dao.web_direction_list import get_all_without_id, delete_by_direction, create_or_update, get_all
from database.sessions import WEB_SESSION_FACTORY
from routers.web_router.web import jinja_router, templates
from utils.utils import require_user

table_keys = [
    "Авиакомпания",
    "Страна отправления",
    "Страна прибытия",
    "Город отправления",
    "Город прибытия",
    "Код города отправления",
    "Код города прибытия",
    "Код авиакомпании",
    "Статус",
    "Рейс"
]


class Direction(BaseModel):
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


async def get_form_context():
    async with WEB_SESSION_FACTORY() as session:
        table_data = await get_all(session)

    table_data_list = []
    for row in table_data:
        table_data_dict = {}
        for column in row.__table__.columns:
            if column.name == "inc":
                continue
            table_data_dict[column.name] = str(getattr(row, column.name))
        table_data_list.append(table_data_dict)

    fields: dict[str, Any] = Direction.model_fields

    if len(table_data_list) == 0:
        table_data_list.append({})
        for name, info in fields.items():
            if name == "inc":
                continue
            table_data_list[0][name] = None

    return {
        "table_data": table_data_list,
        "table_keys": table_keys
    }


@jinja_router.get("/directory_direction", response_class=HTMLResponse)
async def directory_direction(
        request: Request,
        user: str = Depends(require_user),
        form_ctx: Dict[str, List[str]] = Depends(get_form_context),
):
    return templates.TemplateResponse(
        "directory_direction.html",
        {
            "request": request,
            "user": user,
            **form_ctx,
            "error": None,
        }
    )


@jinja_router.post("/save_direction_list")
async def directory_direction_form(
        request: Request,
        user: str = Depends(require_user),
        payload: List[Direction] = Body(..., media_type="application/json"),
        form_ctx: Dict[str, List[str]] = Depends(get_form_context)
):
    print(payload)

    def key_of(d: Direction) -> Tuple[str,str,str]:
        return (
            d.town_of_departure_alias,
            d.town_of_arrival_alias,
            d.airline_alias,
        )

    incoming_keys = {key_of(d) for d in payload}
    async with WEB_SESSION_FACTORY() as session:

        all_direction_records = await get_all(session)

        existing_map = {
            (obj.town_of_departure_alias, obj.town_of_arrival_alias, obj.airline_alias, obj.status, obj.flight_alias): obj
            for obj in all_direction_records
        }
        existing_keys = set(existing_map.keys())

        to_delete = existing_keys - incoming_keys
        to_update = existing_keys & incoming_keys
        to_insert = incoming_keys - existing_keys
        print(to_delete)
        print(to_update)
        print(to_insert)

        if to_delete:
            await delete_by_direction(session=session, list_to_delete=to_delete)

        for d in payload:
            k = key_of(d)
            if k in to_update:
                obj = existing_map[k]
                obj.airline_name = d.airline_name
                obj.country_of_departure = d.country_of_departure
                obj.country_of_arrival = d.country_of_arrival
                obj.town_of_departure = d.town_of_departure
                obj.town_of_arrival = d.town_of_arrival
                obj.status = d.status
                obj.flight_alias = d.flight_alias

        for d in payload:
            k = key_of(d)
            if k in to_update:
                obj = existing_map[k]
                for field, val in d.model_dump().items():
                    setattr(obj, field, val)

        new_rows = [
            d.model_dump()
            for d in payload
            if key_of(d) in to_insert
        ]

        await create_or_update(session=session, new_rows=new_rows)

# TODO: Доделать дизайн модального окна таблицы
