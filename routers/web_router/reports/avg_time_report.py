import os
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Optional

from fastapi import Depends, Form
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, StreamingResponse, Response, FileResponse

from controllers.web.reports.WebAvgTimeReportController import WebAvgTimeReport
from dao.department_dao import get
from database.sessions import KOMPAS_SESSION_FACTORY
from routers.web_router.web import web_jinja_router, templates
from utils.utils import require_user


async def get_form_context() -> Dict[str, List[str]]:

    async with KOMPAS_SESSION_FACTORY() as session:
        department_names_list = [d.name for d in await get(session)]

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


@web_jinja_router.get("/report_avg", response_class=HTMLResponse)
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


@web_jinja_router.post("/report_avg")
async def report_avg_form(
    request: Request,
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
    controller = WebAvgTimeReport(
        date_from=date_from,
        date_till=date_till,
        departments=departments,
        report_type=report_type,
    )
    controller.set_session(KOMPAS_SESSION_FACTORY)

    excel_filepath = await controller.run()

    if not os.path.exists(excel_filepath):
        return {"error": "File not found"}
    return FileResponse(
        excel_filepath,
        filename="downloaded_file.xlsx"
    )
