import json
import os
from datetime import datetime
from typing import List, Dict, Optional

from fastapi import Depends, Form, BackgroundTasks, APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse, FileResponse, RedirectResponse

from controllers.web.reports.WebAvgTimeReportController import WebAvgTimeReport
from dao.samo.department_dao import get
from dao.web.department_schedule_dao import get_distinct_department_inc
from dao.web.download_list_dao import get_download_id
from database.sessions import KOMPAS_SESSION_FACTORY, WEB_SESSION_FACTORY
from routers.web_router.utils import make_route_permission_deps
from routers.web_router.web import web_jinja_router, templates
from utils.utils import require_user, generate_file_path


async def get_form_context() -> Dict[str, List[str]]:

    async with WEB_SESSION_FACTORY() as session:
        distinct_department_inc = await get_distinct_department_inc(session)

    async with KOMPAS_SESSION_FACTORY() as session:
        department_names_list = [d.name for d in await get(session) if d.inc in distinct_department_inc]

    report_types = [
        "AvgTimeReport",
        "AnomalyMsgReport",
        "MoreThanFourHoursAnswerReport",
        "Отчет по среднему времени ответа (агрегированный)"
    ]
    return {
        "departments":  department_names_list,
        "report_types": report_types
    }


async def validate_avg_report_input(
    date_from_str: str,
    date_till_str: str,
    departments: List[str],
    report_type: str
) -> [bool, str | None]:
    if date_from_str == "":
        return False, 'Заполните поле "Дата начала"'
    if date_till_str == "":
        return False, 'Заполните поле "Дата окончания"'

    date_from = datetime.strptime(date_from_str, "%Y-%m-%d")
    date_till = datetime.strptime(date_till_str, "%Y-%m-%d")

    if len(departments) == 0:
        return False, "Нужно выбрать как минимум 1 департамент"

    if report_type is None:
        return False, "Нужно выбрать как минимум 1 тип отчета"

    if date_from > date_till:
        return False, "Дата начала должна быть меньше или равна дате окончания"

    return True, None


avg_time_report_router = APIRouter(
    prefix="/report_avg",
    dependencies=[Depends(make_route_permission_deps('report_avg'))],
    tags=["Отчет по среднему времени ответа"],
)


@avg_time_report_router.get(
    "",
    response_class=HTMLResponse
)
async def report_avg(
    request: Request,
    user: str = Depends(require_user),
    form_ctx: Dict[str, List[str]] = Depends(get_form_context),
):
    return templates.TemplateResponse(
        "report_avg.html",
        {
            "request": request,
            "user": user,
            **form_ctx,
            "selected_date_from": None,
            "selected_date_till": None,
            "selected_departments": [],
            "selected_report_type": None,
            "error": None,
        }
    )


@avg_time_report_router.post("")
async def report_avg_form(
    request: Request,
    background_tasks: BackgroundTasks,
    resource_name: str = 'report_avg',
    date_from: str = Form(...),
    date_till: str = Form(...),
    departments: List[str] = Form([]),
    report_type: Optional[str] = Form(None),
    user: str = Depends(require_user),
    form_ctx: Dict[str, List[str]] = Depends(get_form_context),
):
    validation_result = await validate_avg_report_input(date_from, date_till, departments, report_type)
    if not validation_result[0]:
        msg = validation_result[1]
        return templates.TemplateResponse(
            "report_avg.html",
            {
                "request": request,
                "user": user,
                **form_ctx,
                "selected_date_from": date_from,
                "selected_date_till": date_till,
                "selected_departments": departments,
                "selected_report_type": report_type,
                "error": msg,
            },
            status_code=422
        )
    file_path = generate_file_path(resource_name, user, "xlsx").__str__()
    params_dict = {
        'date_beg_from': date_from or "",
        'date_beg_till': date_till or "",
        'departments': departments or "",
        'report_type': report_type or "",
    }

    params_json = json.dumps(params_dict, ensure_ascii=False)

    async with WEB_SESSION_FACTORY() as session:
        download_id = await get_download_id(
            session,
            user,
            resource_name,
            file_path,
            params_json
        )
    controller = WebAvgTimeReport(
        date_from=date_from,
        date_till=date_till,
        departments=departments,
        report_type=report_type,
        file_path=file_path,
        download_id=download_id
    )
    controller.set_session(KOMPAS_SESSION_FACTORY)

    await controller.run()

    # if not os.path.exists(excel_filepath):
    #     return {"error": "File not found"}
    # return FileResponse(
    #     excel_filepath,
    #     filename="downloaded_file.xlsx"
    # )
    # background_tasks.add_task(
    #     controller.run
    # )
    return RedirectResponse(f"/web/download", status_code=303)


web_jinja_router.include_router(avg_time_report_router)
