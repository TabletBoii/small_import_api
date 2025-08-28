from datetime import datetime, timedelta
import os
import requests
import asyncio
import httpx

from fastapi import Depends, APIRouter
from msal import ConfidentialClientApplication
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request

from dao.web.pbi_report_data_dao import get_pbi_report_data_by_resource_name
from dao.web.powerbi_telemetry_dao import create
from dao.web.role_dao import get_user_permissions
from dao.web.web_user_dao import get_user_by_username
from database.sessions import WEB_SESSION_FACTORY
from models.web.web_pbi_telemetry_model import WebPbiTelemetryModel
from routers.web_router.web import web_jinja_router, templates
from sub_app.msal_app import msal_app
from utils.async_request_utils import safe_json_get
from utils.msal_token_provider import PBITokenProvider
from utils.utils import require_user

BASE = "https://api.powerbi.com/v1.0/myorg"

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
        f"{BASE}/groups/{pbi_report_data.workspace_id}/reports/{pbi_report_data.report_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    resp.raise_for_status()
    report = resp.json()

    token_resp = requests.post(
        f"{BASE}/groups/{pbi_report_data.workspace_id}/reports/{pbi_report_data.report_id}/GenerateToken",
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


async def get_dataset_details(report_name):
    access_token = pbi_token_provider.get_token()

    headers = {"Authorization": f"Bearer {access_token}"}

    async with WEB_SESSION_FACTORY() as session:
        pbi_report_data = await get_pbi_report_data_by_resource_name(session, report_name)

    group_id = pbi_report_data.workspace_id
    report_id = pbi_report_data.report_id

    async with httpx.AsyncClient(base_url=BASE, headers=headers, timeout=30.0) as client:

        dataset_data_response = await client.get(f"/groups/{group_id}/reports/{report_id}")
        dataset_data_response.raise_for_status()
        dataset_data_json = dataset_data_response.json()
        dataset_id = dataset_data_json.get("datasetId")
        if not dataset_id:
            raise RuntimeError("У отчёта нет datasetId (возможно, paginated/RDL).")

        schedule_task = safe_json_get(client, f"/groups/{group_id}/datasets/{dataset_id}/refreshSchedule")
        refreshes_task = safe_json_get(client, f"/groups/{group_id}/datasets/{dataset_id}/refreshes?$top=1")

        schedule_json, refreshes_json = await asyncio.gather(
            schedule_task, refreshes_task
        )

        return schedule_json, refreshes_json


pbi_router = APIRouter(
    prefix="/power_bi_base",
    dependencies=[Depends(power_bi_routes_permission_deps)],
    tags=["Отчеты PowerBI"],
)


@pbi_router.get("/embed-params/{route_param}")
async def embed_params(
        route_param: str,
        user: str = Depends(require_user)
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
    report_update_details, last_update_json = await get_dataset_details(route_param)
    if len(last_update_json["value"]) == 0:
        last_update_date_value = None
    else:
        last_update_date_value = last_update_json["value"][0].get("endTime", None)

    if last_update_date_value is not None:
        last_update_date = datetime.fromisoformat(last_update_date_value.replace('Z', '+00:00')) + timedelta(hours=5)
        last_update_status = last_update_json["value"][0]["status"]
    elif len(last_update_json["value"]) == 0 and last_update_date_value is None:
        last_update_date = 'Не обновлено'
        last_update_status = "Автоматическое обновление не настроено"
    else:
        last_update_status = last_update_json["value"][0]["status"]
        last_update_date = 'Обновление'

    report_update_times = []
    for time in report_update_details["times"]:
        ua_time = datetime.strptime(time, "%H:%M") - timedelta(hours=2)
        ua_time_str = ua_time.strftime("%H:%M")
        report_update_times.append((time, ua_time_str))
    return templates.TemplateResponse(
        "power_bi_base.html",
        {
            "request": request,
            "user": user,
            "data": route_param,
            "error": None,
            "update_times": report_update_times,
            "last_update_date": last_update_date.strftime("%Y-%m-%d %H:%M") if last_update_date not in ('Обновление','Не обновлено') else last_update_date,
            "last_update_status": last_update_status,
        }
    )


@pbi_router.post("/telemetry/{route_param}")
async def power_bi_telemetry(
        request: Request,
        route_param: str,
        user=Depends(require_user)
):
    data = await request.json()
    data_dict = dict(data)
    create_date_str = data_dict.get("ts")
    create_date = datetime.fromisoformat(create_date_str.replace('Z', '+00:00'))
    async with WEB_SESSION_FACTORY() as session:
        user_instance = await get_user_by_username(session, user)
        report_instance = await get_pbi_report_data_by_resource_name(session, route_param)
        await create(session, WebPbiTelemetryModel(
            user_inc=user_instance.inc,
            report_id=report_instance.id,
            type=data_dict.get("type"),
            page_title=data_dict.get("pageTitle", None),
            create_date=create_date
        ))


web_jinja_router.include_router(pbi_router)
