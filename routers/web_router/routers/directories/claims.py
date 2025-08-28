import json
from typing import Optional, Dict, List

from fastapi import Depends, Form, BackgroundTasks, APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from controllers.web.directories.ClaimDirectoryController import ClaimDirectoryController
from dao.samo.claim_procedure import title_alias_dict
from dao.web.download_list_dao import get_download_id
from database.sessions import KOMPAS_SESSION_FACTORY, WEB_SESSION_FACTORY
from routers.web_router.navigator.navigator_base import Navigator
from routers.web_router.routers.directories.base import directories_router
from routers.web_router.utils import make_route_permission_deps
from routers.web_router.web_base import templates, navigation
from utils.utils import require_user, generate_file_path


main_fields = [
    "Код заказчика",
    "Дата/время расчёта заявки",
    "Дата расчёта заявки",
    "Заявка №",
    "Подтверждение",
    "Тип заявки",
    "Тур: Вид тура",
    "Статус заявки",
    "Основная страна пребывания",
    "Город",
    # "Код города",
    "Заказчик",
    "Дата начала тура",
    "Дата окончания тура",
    "Ночей",
    "Тур",
    "Дней до начала тура",
    # "Заказ: Гостиница",
    # "ФИО 1-го туриста",
    "Взрослых",
    "Детей",
    # "Младенцев",
    "Всего пассажиров",
    "Комиссия (%)",
    # "Ранняя комиссия (%)",
    "По каталогу",
    "К оплате",
    "$",
    "Сумма комиссии",
    # "% частичной оплаты",
    "Оплачено",
    "Внутреннее примечание",
    # "Долг (%)",
    "Долг",
    "Прибыль",
    "Скидка",
    "Бонус",
    # "Дата/время создания заявки",
    "Дата подтверждения/неподтверждения",
    # "Дата выставления счета агенту",
    # "Дата предполагаемой частичной оплаты",
    # "Дата предполагаемой оплаты",
    # "Нужен счет",
    # "Имя интернет-пользователя",
    "Телефоны заказчика",
    # "Дата спец. предложения",
    # "Номер СПО",
    # "Штраф",
    # "Прибыль (%)",
    # "Тип программы",
    "Куратор"
]


async def get_form_context() -> Dict[str, List[str]]:

    field_list = [
        field for field in title_alias_dict.keys()
    ]

    return {
        "field_list":  field_list,
        "main_fields": main_fields
    }


async def validate_selected_dates(
    datebeg_from: str,
    datebeg_till: str,
    cdate_from: str,
    cdate_till: str,
    confirmdate_from: str,
    confirmdate_till: str,
    rdate_from: str,
    rdate_till: str,
) -> (bool, str):
    date_names = ["начала тура", "расчета заявки", "подтверждения заявки", "создания заявки"]

    pairs = [
        (datebeg_from,   datebeg_till),
        (cdate_from,     cdate_till),
        (confirmdate_from, confirmdate_till),
        (rdate_from,     rdate_till),
    ]

    if all(not date_from and not date_till for date_from, date_till in pairs):
        return False, "Хотя бы одна дата должна быть выбрана"

    for index, (date_from, date_till) in enumerate(pairs):
        if bool(date_from) ^ bool(date_till):
            return False, f"Обе даты {date_names[index]} должны быть заполнены"

    return True, ""


async def validate_avg_report_input(
    datebeg_from: str,
    datebeg_till: str,
    cdate_from: str,
    cdate_till: str,
    confirmdate_from: str,
    confirmdate_till: str,
    rdate_from: str,
    rdate_till: str,
    selected_fields_list: List[str]
):
    date_validation_result = await validate_selected_dates(
        datebeg_from,
        datebeg_till,
        cdate_from,
        cdate_till,
        confirmdate_from,
        confirmdate_till,
        rdate_from,
        rdate_till,
    )
    if not date_validation_result[0]:
        return False, date_validation_result[1]

    if len(selected_fields_list) == 0:
        return False, "Нужно выбрать как минимум 1 поле"

    return True, None


claims_router = APIRouter(
    prefix=navigation.directories.directory_claims.path,
    dependencies=[Depends(make_route_permission_deps('directory_claims'))],
    tags=["Справочник заявок"],
)


@claims_router.get(
    navigation.directories.directory_claims.template.path,
    response_class=HTMLResponse
)
async def directory_claims(
    request: Request,
    user: str = Depends(require_user),
    form_ctx: Dict[str, List[str]] = Depends(get_form_context),
):
    return templates.TemplateResponse(
        "directory_claims.html",
        {
            "request": request,
            "user": user,
            **form_ctx,
            "selected_date_beg_from": None,
            "selected_date_beg_till": None,
            "selected_claim_create_date_from": None,
            "selected_claim_create_date_till": None,
            "selected_confirm_date_from": None,
            "selected_confirm_date_till": None,
            "selected_r_date_from": None,
            "selected_r_date_till": None,
            "selected_field_list": [],
            "error": None,
        }
    )


@claims_router.post(navigation.directories.directory_claims.form.path)
async def directory_claims_form(
    request: Request,
    background_tasks: BackgroundTasks,
    user: str = Depends(require_user),
    resource_name: str = 'directory_claims',
    form_ctx: Dict[str, List[str]] = Depends(get_form_context),
    date_beg_from: Optional[str] = Form(...),
    date_beg_till: Optional[str] = Form(...),
    claim_create_date_from: Optional[str] = Form(...),
    claim_create_date_till: Optional[str] = Form(...),
    confirm_date_from: Optional[str] = Form(...),
    confirm_date_till: Optional[str] = Form(...),
    r_date_from: Optional[str] = Form(...),
    r_date_till: Optional[str] = Form(...),
    field_list: list[str] = Form([])
):

    validation_result = await validate_avg_report_input(
        date_beg_from,
        date_beg_till,
        claim_create_date_from,
        claim_create_date_till,
        confirm_date_from,
        confirm_date_till,
        r_date_from,
        r_date_till,
        field_list
    )
    if not validation_result[0]:
        msg = validation_result[1]
        return templates.TemplateResponse(
            "directory_claims.html",
            {
                "request": request,
                "user": user,
                **form_ctx,
                "selected_date_beg_from": date_beg_from,
                "selected_date_beg_till": date_beg_till,
                "selected_claim_create_date_from": claim_create_date_from,
                "selected_claim_create_date_till": claim_create_date_till,
                "selected_confirm_date_from": confirm_date_from,
                "selected_confirm_date_till": confirm_date_till,
                "selected_r_date_from": r_date_from,
                "selected_r_date_till": r_date_till,
                "selected_field_list": field_list,
                "error": msg,
            },
            status_code=422
        )
    file_path = generate_file_path(resource_name, user, "xlsx").__str__()
    params_dict = {
        'date_beg_from': date_beg_from or "",
        'date_beg_till': date_beg_till or "",
        'claim_create_date_from': claim_create_date_from or "",
        'claim_create_date_till': claim_create_date_till or "",
        'confirm_date_from': confirm_date_from or "",
        'confirm_date_till': confirm_date_till or "",
        'r_date_from': r_date_from or "",
        'r_date_till': r_date_till or "",
        'field_list': field_list,
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

    controller = ClaimDirectoryController(
        date_beg_from=date_beg_from,
        date_beg_till=date_beg_till,
        claim_create_date_from=claim_create_date_from,
        claim_create_date_till=claim_create_date_till,
        confirm_date_from=confirm_date_from,
        confirm_date_till=confirm_date_till,
        r_date_from=r_date_from,
        r_date_till=r_date_till,
        field_list=field_list,
        file_path=file_path,
        download_id=download_id
    )
    controller.set_session(KOMPAS_SESSION_FACTORY)
    # background_tasks.add_task(
    #     controller.run
    # )
    # await controller.streaming_run()
    background_tasks.add_task(
        controller.streaming_run
    )
    return RedirectResponse(f"/web/download", status_code=303)
