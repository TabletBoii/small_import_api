from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse

from dao.web.access_request_dao import get_pending_requests, request_rejection, request_confirmation
from database.sessions import WEB_SESSION_FACTORY
from routers.admin_router.admin import admin_jinja_router
from routers.templates import admin_templates

admin_access_request_router = APIRouter(
    prefix="/access_request",
    tags=["Запросы доступа"],
)


async def form_ctx():
    async with WEB_SESSION_FACTORY() as session:
        pending_access_request_list = await get_pending_requests(session)
    for i in range(len(pending_access_request_list)):
        pending_access_request_list[i] = dict(pending_access_request_list[i])
        pending_access_request_list[i]['request_date'] = str(pending_access_request_list[i]['request_date'])
    return {
        "headers": [
            "ID",
            "Пользователь",
            "Ресурс",
            "Описание",
            "Дата"
        ],
        "pending_access_request_list": pending_access_request_list
    }


@admin_access_request_router.get("")
async def admin_access_request(
        request: Request,
        ctx=Depends(form_ctx)
):
    return admin_templates.TemplateResponse(
        "access_request.html",
        {
            "request": request,
            **ctx
        }
    )


@admin_access_request_router.get("/confirm/{request_id}")
async def confirm_access_request(
        request: Request,
        request_id: int
):
    async with WEB_SESSION_FACTORY() as session:
        await request_confirmation(session, request_id)

    return RedirectResponse(f"/admin/access_request", status_code=303)


@admin_access_request_router.post("/reject/{request_id}")
async def reject_access_request(
        request: Request,
        request_id: int
):
    rejection_reason = dict(await request.form())["rejection_reason"]
    async with WEB_SESSION_FACTORY() as session:
        await request_rejection(session, request_id, rejection_reason)

    return RedirectResponse(f"/admin/access_request", status_code=303)

admin_jinja_router.include_router(admin_access_request_router)
