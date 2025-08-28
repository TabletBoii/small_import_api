from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse

from enums.user_resource_permission_enum import UserPermissionResourceTypeEnum
from routers.web_router.navigator.navigator_base import Navigator
from routers.web_router.web_base import templates, make_user_permission_deps, navigation
from utils.utils import require_user

directories_router = APIRouter(
    prefix=navigation.directories.path,
    tags=["Справочники"],
)


@directories_router.get(navigation.directories.index.path, response_class=HTMLResponse)
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
