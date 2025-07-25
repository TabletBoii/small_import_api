import os
import sys

from fastapi import Request, Depends, APIRouter
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from dao.web.web_role_dao import get_user_permissions
from database.sessions import WEB_SESSION_FACTORY

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
        permissions=Depends(make_user_permission_deps(1))
):
    return templates.TemplateResponse("reports.html", {"request": request, "user": user, "permissions": permissions})


@web_jinja_router.get("/directories", response_class=HTMLResponse)
async def directories(
        request: Request,
        user: str = Depends(require_user),
        permissions=Depends(make_user_permission_deps(2))
):
    return templates.TemplateResponse("directories.html",
                                      {"request": request, "user": user, "permissions": permissions})


# Не удалять импорты - все маршруты идут от этих импортов
##################################
from .reports import avg_time_report
from .reports import report_dmc
from .directories import claims
from .directories import direction
from .directories import departments
from . import auth
from . import download_page
##################################
