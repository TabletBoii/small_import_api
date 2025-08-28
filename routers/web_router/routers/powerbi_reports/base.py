from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse

from enums.user_resource_permission_enum import UserPermissionResourceTypeEnum
from routers.web_router.web_base import templates, make_user_permission_deps, navigation
from utils.utils import require_user

powerbi_router = APIRouter(
    prefix=navigation.powerbi_base.path,
    tags=["Отчеты PowerBI"],
)


@powerbi_router.get(navigation.powerbi_base.power_bi.path, response_class=HTMLResponse)
async def power_bi(
        request: Request,
        user: str = Depends(require_user),
        permissions=Depends(make_user_permission_deps(UserPermissionResourceTypeEnum.POWER_BI_REPORT.value))
):
    return templates.TemplateResponse(
        "list_page.html",
        {
            "request": request,
            "user": user,
            "page_title": "Отчеты PowerBI",
            "permissions": permissions,
            "route_name": "power_bi_base"
        }
    )
