from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse

from enums.user_resource_permission_enum import UserPermissionResourceTypeEnum
from routers.web_router.web_base import make_user_permission_deps, templates, navigation
from utils.utils import require_user

from enum import Enum


reports_router = APIRouter(
    prefix=navigation.reports.path,
    tags=["Отчеты"],
)


@reports_router.get(navigation.reports.index.path, response_class=HTMLResponse)
async def reports(
        request: Request,
        user: str = Depends(require_user),
        permissions=Depends(make_user_permission_deps(UserPermissionResourceTypeEnum.REPORT.value))
):
    return templates.TemplateResponse(
        "list_page.html",
        {
            "request": request,
            "user": user,
            "page_title": "Отчеты",
            "permissions": permissions,
            "route_name": None
        }
    )
