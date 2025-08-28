from datetime import datetime

from fastapi import Depends, Form, Query, APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

from dao.samo.country_dao import get_country_name_offset
from dao.samo.partner_dao import get_partner_name_offset
from database.sessions import KOMPAS_SESSION_FACTORY
from routers.web_router.routers.reports.base import reports_router
from routers.web_router.utils import make_route_permission_deps
from routers.web_router.web_base import templates, navigation
from utils.utils import require_user

#
# async def get_form_context() -> Dict[str, List[str]]:
#
#     async with KOMPAS_SESSION_FACTORY() as session:
#         department_names_list = [d.name for d in await get(session)]
#
#     report_types = [
#         "AvgTimeReport",
#         "AnomalyMsgReport",
#         "MoreThanFourHoursAnswerReport",
#         "Отчет по среднему времени ответа (агрегированный)"
#     ]
#     return {
#         "departments":  department_names_list,
#         "report_types": report_types
#     }


async def validate_avg_report_input(
    date_from_str_p1: str,
    date_till_str_p1: str,
    date_from_str_p2: str,
    date_till_str_p2: str,
    country: str,
    partner: str
) -> [bool, str | None]:
    if partner == "":
        return False, 'Выберите партнера'
    if country == "":
        return False, 'Выберите страну'
    if date_from_str_p1 == "":
        return False, 'Заполните поле Дата начала(Период 1)'
    if date_till_str_p1 == "":
        return False, 'Заполните поле Дата окончания(Период 1)'

    if date_from_str_p2 == "":
        return False, 'Заполните поле Дата начала(Период 2)'
    if date_till_str_p2 == "":
        return False, 'Заполните поле Дата окончания(Период 2)'

    date_from_p1 = datetime.strptime(date_from_str_p1, "%Y-%m-%d")
    date_till_p1 = datetime.strptime(date_till_str_p1, "%Y-%m-%d")

    date_from_p2 = datetime.strptime(date_from_str_p2, "%Y-%m-%d")
    date_till_p2 = datetime.strptime(date_till_str_p2, "%Y-%m-%d")

    if date_from_p1 > date_till_p1:
        return False, "Дата начала(Период 1) должна быть меньше или равна дате окончания(Период 1)"

    if date_from_p2 > date_till_p2:
        return False, "Дата начала(Период 2) должна быть меньше или равна дате окончания(Период 2)"

    return True, None


dmc_report_router = APIRouter(
    prefix=navigation.reports.report_dmc.path,
    dependencies=[Depends(make_route_permission_deps('report_dmc'))],
    tags=["Отчет по партнерам DMC"],
)


@dmc_report_router.get(
    navigation.reports.report_dmc.template.path,
    response_class=HTMLResponse
)
async def report_dmc(
    request: Request,
    user: str = Depends(require_user)
):
    return templates.TemplateResponse(
        "report_dmc.html",
        {
            "request": request,
            "user": user,
            "selected_date_from_p1": None,
            "selected_date_till_p1": None,
            "selected_date_from_p2": None,
            "selected_date_till_p2": None,
            "selected_partnerFilter": None,
            "selected_countryFilter": None,
            "error": None,
        }
    )


@dmc_report_router.post(navigation.reports.report_dmc.form.path)
async def report_dmc_form(
    request: Request,
    date_from_p1: str = Form(...),
    date_till_p1: str = Form(...),
    date_from_p2: str = Form(...),
    date_till_p2: str = Form(...),
    partnerFilter_input: str = Form(...),
    countryFilter_input: str = Form(...),
    user: str = Depends(require_user),
    # form_ctx: Dict[str, List[str]] = Depends(get_form_context),
):
    validation_result = await validate_avg_report_input(
        date_from_p1,
        date_till_p1,
        date_from_p2,
        date_till_p2,
        countryFilter_input,
        partnerFilter_input
    )
    print(date_from_p1)
    print(date_till_p1)
    print(date_from_p2)
    print(date_till_p2)
    print(countryFilter_input)
    print(partnerFilter_input)
    if not validation_result[0]:
        msg = validation_result[1]
        return templates.TemplateResponse(
            "report_dmc.html",
            {
                "request": request,
                "user": user,
                # **form_ctx,
                "selected_date_from_p1": date_from_p1,
                "selected_date_till_p1": date_till_p1,
                "selected_date_from_p2": date_from_p2,
                "selected_date_till_p2": date_till_p2,
                "selected_countryFilter": countryFilter_input,
                "selected_partnerFilter": partnerFilter_input,
                "error": msg,
            },
            status_code=422
        )
    # controller = WebAvgTimeReport(
    #     date_from=date_from,
    #     date_till=date_till,
    #     departments=departments,
    #     report_type=report_type,
    # )
    # controller.set_session(KOMPAS_SESSION_FACTORY)
    #
    # excel_filepath = await controller.run()
    #
    # if not os.path.exists(excel_filepath):
    #     return {"error": "File not found"}
    # return FileResponse(
    #     excel_filepath,
    #     filename="downloaded_file.xlsx"
    # )


@dmc_report_router.get(navigation.reports.report_dmc.partner_filter.path)
async def report_dmc_partner_filter(
    q: str = Query("", title="Поисковый запрос"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):

    async with KOMPAS_SESSION_FACTORY() as session:
        items = await get_partner_name_offset(
            session=session,
            query=q,
            offset=skip,
            limit=limit
        )
    return {
        "items": [{"id": i.inc, "name": i.name} for i in items],
    }


@dmc_report_router.get(navigation.reports.report_dmc.country_filter.path)
async def report_dmc_country_filter(
    q: str = Query("", title="Поисковый запрос"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    async with KOMPAS_SESSION_FACTORY() as session:
        items = await get_country_name_offset(
            session=session,
            query=q,
            offset=skip,
            limit=limit
        )
    return {
        "items": [{"id": i.inc, "name": i.name} for i in items],
    }
