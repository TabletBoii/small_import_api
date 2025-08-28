import dataclasses
import os
import sys
from enum import StrEnum, Enum

from fastapi import Request, Depends, APIRouter
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse

from dao.web.role_dao import get_user_permissions
from database.sessions import WEB_SESSION_FACTORY
from enums.user_resource_permission_enum import UserPermissionResourceTypeEnum
from routers.web_router.navigator.navigator_base import Navigator

from utils.utils import require_user

script_path = os.path.abspath(sys.argv[0])
script_dir = os.path.dirname(script_path)
templates = Jinja2Templates(directory="templates/web")

navigation = Navigator()

templates.env.globals["navigation"] = navigation
navigation.powerbi_base.power_bi_base_actions.power_bi_telemetry

_web_router = APIRouter()


def make_user_permission_deps(page_type: int):
    async def user_permission_deps(
        user: str = Depends(require_user),
    ):
        async with WEB_SESSION_FACTORY() as session:
            perms = await get_user_permissions(session, user)
        allowed = [(perm["resource"], perm["has_access"], perm["name_cirill"], perm["description"]) for perm in perms if perm["resource_type"] == page_type]

        return allowed

    return user_permission_deps


@_web_router.get("/")
async def web_home(
        request: Request,
        user: str = Depends(require_user)
):
    return RedirectResponse(url="/web/home", status_code=302)


@_web_router.get(navigation.home.path)
async def web_home(
        request: Request,
        user: str = Depends(require_user)
):
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "user": user}
    )

base_router = _web_router
