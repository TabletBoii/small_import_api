import os
from typing import Optional, Dict, List

from fastapi import Depends, Form
from starlette.requests import Request
from starlette.responses import HTMLResponse, FileResponse

from controllers.web.directories.ClaimDirectoryController import ClaimDirectoryController
from dao.claim_procedure import ClaimProcedure, title_alias_dict
from database.sessions import KOMPAS_SESSION_FACTORY
from routers.web_router.web import jinja_router, templates
from utils.utils import require_user


async def get_form_context() -> Dict[str, List[str]]:

    field_list = [
        field for field in title_alias_dict.keys()
    ]

    return {
        "field_list":  field_list
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


@jinja_router.get("/directory_claims", response_class=HTMLResponse)
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


@jinja_router.post("/directory_claims")
async def directory_claims_form(
    request: Request,
    user: str = Depends(require_user),
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
    )
    controller.set_session(KOMPAS_SESSION_FACTORY)
    resulted_file_path = await controller.run()

    if not os.path.exists(resulted_file_path):
        return {"error": "File not found"}
    return FileResponse(
        resulted_file_path,
        filename="downloaded_file.xlsx"
    )
