from fastapi import Depends, APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

from routers.web_router.navigator.navigator_base import Navigator
from routers.web_router.routers.directories.base import directories_router
from routers.web_router.utils import make_route_permission_deps
from routers.web_router.web_base import templates, navigation
from utils.utils import require_user


department_directory_router = APIRouter(
    prefix=navigation.directories.department_directory.path,
    dependencies=[Depends(make_route_permission_deps('department_directory'))],
    tags=["Справочник партнеров"],
)


@department_directory_router.get(
    navigation.directories.department_directory.template.path,
    response_class=HTMLResponse,
    dependencies=[Depends(make_route_permission_deps('department_directory'))]
)
async def department_directory(
        request: Request,
        user: str = Depends(require_user),
        # form_ctx: Dict[str, List[str]] = Depends(get_form_context),
):
    return templates.TemplateResponse(
        "department_directory.html",
        {
            "request": request,
            "user": user,
            # **form_ctx,
            "error": None,
        }
    )
