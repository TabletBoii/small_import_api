import datetime
from collections import defaultdict
from time import strptime

from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse

from dao.samo.department_dao import get, get_dict
from dao.web.department_schedule_dao import get_department_schedule, insert_all, merge_department_schedule
from database.sessions import KOMPAS_SESSION_FACTORY, WEB_SESSION_FACTORY
from models.web.department_schedule_model import DepartmentScheduleModel
from routers.admin_router.admin import admin_jinja_router
from routers.templates import admin_templates
from utils.utils import _to_time_or_none

admin_department_schedule_router = APIRouter(
    prefix="/department_schedule",
    tags=["Расписание департаментов"],
)


async def form_ctx():
    async with KOMPAS_SESSION_FACTORY() as session:
        department_list = await get_dict(session)

    async with WEB_SESSION_FACTORY() as session:
        schedule_list = await get_department_schedule(session)

    dept_schedule_dict = defaultdict(dict)
    for schedule in schedule_list:

        day_code = schedule["week_day"]
        dept_schedule_dict[schedule["department_inc"]][day_code] = {
            "start": schedule["start_time"],
            "end": schedule["end_time"],
        }
    return {
        "departments": department_list,
        "schedule": dict(dept_schedule_dict)
    }


@admin_department_schedule_router.get("")
async def admin_department_schedule(
        request: Request,
        ctx=Depends(form_ctx)
):
    return admin_templates.TemplateResponse(
        "department_schedule.html",
        {
            "request": request,
            **ctx
        }
    )


@admin_department_schedule_router.post("/save_schedule")
async def admin_save_schedule(
        request: Request
):
    form_data = await request.form()
    form_data = dict(form_data)
    parsed_data = defaultdict(dict)
    for key, value in form_data.items():
        split_str = key.split("[")
        for index, split_item in enumerate(split_str):
            split_str[index] = split_item.replace("]", "")
        if parsed_data[split_str[1]].get(split_str[2], None) is not None:
            parsed_data[split_str[1]][split_str[2]][split_str[3]] = value
        else:
            parsed_data[split_str[1]].update({
                split_str[2]: {
                    split_str[3]: value
                }
            })
    models: list[DepartmentScheduleModel] = []
    for dept_key, days in parsed_data.items():
        dept_id = int(dept_key)
        for day_code, cell in (days or {}).items():
            st = _to_time_or_none(cell.get('start'))
            en = _to_time_or_none(cell.get('end'))
            if st is None or en is None:
                continue
            models.append(DepartmentScheduleModel(
                department_inc=dept_id,
                week_day=day_code,
                start_time=st,
                end_time=en,
            ))

    async with WEB_SESSION_FACTORY() as session:
        await merge_department_schedule(session, models)

    return RedirectResponse("/admin/department_schedule", status_code=303)

admin_jinja_router.include_router(admin_department_schedule_router)

