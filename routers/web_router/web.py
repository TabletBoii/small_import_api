import os
import sys

from fastapi import Request, Depends, APIRouter
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse

from dao.web.role_dao import get_user_permissions
from database.sessions import WEB_SESSION_FACTORY
from enums.user_resource_permission_enum import UserPermissionResourceTypeEnum

from utils.utils import require_user

script_path = os.path.abspath(sys.argv[0])
script_dir = os.path.dirname(script_path)
templates = Jinja2Templates(directory="templates/web")

web_jinja_router = APIRouter()


def make_user_permission_deps(page_type: int):
    async def user_permission_deps(
        user: str = Depends(require_user),
    ):
        async with WEB_SESSION_FACTORY() as session:
            perms = await get_user_permissions(session, user)
        allowed = [(perm["resource"], perm["has_access"], perm["name_cirill"], perm["description"]) for perm in perms if perm["resource_type"] == page_type]

        return allowed

    return user_permission_deps


@web_jinja_router.get("/")
async def web_home(
        request: Request,
        user: str = Depends(require_user)
):
    return RedirectResponse(url="/web/home", status_code=302)


@web_jinja_router.get("/home")
async def web_home(
        request: Request,
        user: str = Depends(require_user)
):
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "user": user}
    )


@web_jinja_router.get("/reports", response_class=HTMLResponse)
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
    # return templates.TemplateResponse("reports.html", {"request": request, "user": user, "permissions": permissions})


@web_jinja_router.get("/directories", response_class=HTMLResponse)
async def directories(
        request: Request,
        user: str = Depends(require_user),
        permissions=Depends(make_user_permission_deps(UserPermissionResourceTypeEnum.DIRECTORY.value))
):
    return templates.TemplateResponse(
        "list_page.html",
        {
            "request": request,
            "user": user,
            "page_title": "Справочники",
            "permissions": permissions,
            "route_name": None
        }
    )


@web_jinja_router.get("/power_bi", response_class=HTMLResponse)
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


# Не удалять импорты - все маршруты идут от этих импортов
##################################
from .reports import avg_time_report
from .reports import report_dmc
from .directories import claims
from .directories import direction
from .directories import departments
from . import auth
from . import download_page
from . import powerbi_base
##################################
