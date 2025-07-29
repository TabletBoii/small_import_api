from typing import Dict, List

from fastapi import Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse

from routers.web_router.utils import make_route_permission_deps
from routers.web_router.web import web_jinja_router, templates
from utils.utils import require_user


@web_jinja_router.get(
    "/department_directory",
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
