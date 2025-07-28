from typing import Dict, List, Tuple, Any

from fastapi import Depends, Body
from starlette.requests import Request
from starlette.responses import HTMLResponse

from dao.web.web_direction_list import get_all, delete_by_inc, update_by_inc, create
from database.sessions import WEB_SESSION_FACTORY
from pydantic_models.web_models import Direction
from routers.web_router.utils import make_route_permission_deps
from routers.web_router.web import web_jinja_router, templates
from utils.utils import require_user

table_keys = [
    "ID",
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


async def get_form_context():
    async with WEB_SESSION_FACTORY() as session:
        table_data = await get_all(session)

    table_data_list = []
    for row in table_data:
        table_data_dict = {"inc": row.inc}
        for column in row.__table__.columns:
            if column.name == "inc":
                continue
            table_data_dict[column.name] = str(getattr(row, column.name))
        table_data_list.append(table_data_dict)

    fields: dict[str, Any] = Direction.model_fields

    if len(table_data_list) == 0:
        table_data_list.append({})
        for name, info in fields.items():
            table_data_list[0][name] = None

    return {
        "table_data": table_data_list,
        "table_keys": table_keys
    }


@web_jinja_router.get(
    "/directory_direction",
    response_class=HTMLResponse,
    dependencies=[Depends(make_route_permission_deps("directory_direction"))]
)
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


@web_jinja_router.post(
    "/save_direction_list"
)
async def directory_direction_form(
        request: Request,
        user: str = Depends(require_user),
        payload: List[Direction] = Body(..., media_type="application/json"),
        form_ctx: Dict[str, List[str]] = Depends(get_form_context)
):
    def key_of(d: Direction) -> Tuple[int, str, str, str, str, str, str]:
        return (
            d.inc,
            d.airline_name,
            d.town_of_departure_alias,
            d.town_of_arrival_alias,
            d.airline_alias,
            d.status,
            d.flight_alias
        )

    async with WEB_SESSION_FACTORY() as session:

        all_direction_records = await get_all(session)

        existing_by_inc: Dict[int, Direction] = {
            obj.inc: obj
            for obj in all_direction_records
            if obj.inc
        }

        new_records = [d for d in payload if d.inc == 0]
        incoming_nonzero = {d.inc for d in payload if d.inc != 0}

        to_delete = [
            inc
            for inc in (set(existing_by_inc) - incoming_nonzero)
        ]

        to_insert = new_records

        to_update = []
        for d in payload:
            if d.inc != 0:
                existing = existing_by_inc.get(d.inc)
                if not existing:
                    to_insert.append(d)
                elif key_of(d) != key_of(existing):
                    to_update.append(d)

        if len(to_delete) != 0:
            await delete_by_inc(session=session, inc_list_to_delete=to_delete)

        if len(to_update) != 0:
            await update_by_inc(session=session, inc_list_to_update=to_insert)

        if len(to_insert) != 0:
            await create(session=session, list_to_create=to_insert)
