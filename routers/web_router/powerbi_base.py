import os
import requests

from fastapi import Depends, APIRouter
from msal import ConfidentialClientApplication
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request

from dao.web.web_pbi_report_data_dao import get_pbi_report_data_by_resource_name
from dao.web.web_role_dao import get_user_permissions
from database.sessions import WEB_SESSION_FACTORY
from routers.web_router.web import web_jinja_router, templates
from sub_app.msal_app import msal_app
from utils.msal_token_provider import PBITokenProvider
from utils.utils import require_user

WORKSPACE_ID = os.getenv("PBI_WORKSPACE_ID")
REPORT_ID = os.getenv("PBI_REPORT_ID")

pbi_token_provider = PBITokenProvider(
    app=msal_app,
    scopes=["https://analysis.windows.net/powerbi/api/.default"],
    cache_file="tokens/pbi_token.json",
    expiry_buffer=300,
)


async def power_bi_routes_permission_deps(
        request: Request,
        user: str = Depends(require_user),
):
    route_param = request.path_params.get("route_param")

    async with WEB_SESSION_FACTORY() as session:
        perms = await get_user_permissions(session, user)

    if not any(p["resource"] == route_param and p["has_access"] for p in perms):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Нет доступа к ресурсу {route_param}"
        )
    return True


async def get_embed_params(report_name: str):
    access_token = pbi_token_provider.get_token()

    async with WEB_SESSION_FACTORY() as session:
        pbi_report_data = await get_pbi_report_data_by_resource_name(session, report_name)

    resp = requests.get(
        f"https://api.powerbi.com/v1.0/myorg/groups/{pbi_report_data.workspace_id}/reports/{pbi_report_data.report_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    resp.raise_for_status()
    report = resp.json()

    token_resp = requests.post(
        f"https://api.powerbi.com/v1.0/myorg/groups/{pbi_report_data.workspace_id}/reports/{pbi_report_data.report_id}/GenerateToken",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json={"accessLevel": "View"}
    )
    token_resp.raise_for_status()
    embed_info = token_resp.json()

    return {
        "embedUrl": report["embedUrl"],
        "embedToken": embed_info["token"],
        "expiration": embed_info["expiration"]
    }


pbi_router = APIRouter(
    prefix="/power_bi_base",
    dependencies=[Depends(power_bi_routes_permission_deps)],
    tags=["Отчеты PowerBI"],
)


@pbi_router.get("/embed-params/{route_param}")
async def embed_params(
    route_param: str
):
    return await get_embed_params(route_param)


@pbi_router.get(
    "/{route_param}"
)
async def power_bi_base(
        request: Request,
        route_param: str,
        user: str = Depends(require_user)
):
    return templates.TemplateResponse(
        "power_bi_base.html",
        {
            "request": request,
            "user": user,
            "data": route_param,
            "error": None,
        }
    )

web_jinja_router.include_router(pbi_router)
