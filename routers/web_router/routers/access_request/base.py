from typing import Dict, List, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import InstrumentedAttribute
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from dao.web.access_request_dao import create, access_requests_by_username
from dao.web.resource_dao import get_resource_list, get_resource_type_list, get_resource_list_with_user_access
from dao.web.web_user_dao import get_user_by_username
from database.sessions import WEB_SESSION_FACTORY
from models.web.web_access_request_model import WebAccessRequestModel
from routers.web_router.navigator.navigator_base import Navigator
from routers.web_router.web_base import templates, navigation
from utils.utils import require_user

access_request_router = APIRouter(
    prefix=navigation.access_request.path,
    tags=["Запрос доступа"],
)


async def get_form_context(user: str) -> dict[str, dict[Any, list[Any]]]:

    async with WEB_SESSION_FACTORY() as session:
        resource_list = await get_resource_list_with_user_access(session, user)
        resource_type_list = [d.name_cirill for d in await get_resource_type_list(session)]
        users_access_requests = await access_requests_by_username(session, user)
    resulted_resource_list = []
    print(resource_list)
    for resource in resource_list:
        resulted_resource_list.append({
            "inc": resource[0],
            "name": resource[1],
            "type": resource[2],
            "name_cirill": resource[3],
            "description": resource[4],
            "has_access": resource[5]
        })
    print(resulted_resource_list)
    resource_dict = {}
    for resource_type in resource_type_list:
        resource_dict[resource_type] = []
        for resource in resulted_resource_list:
            if resource.get("type") == resource_type:
                resource_dict[resource_type].append(resource)
    print(resource_dict)
    return {
        "resource_dict":  resource_dict,
        "users_access_requests": users_access_requests,
        "headers": [
            "ID",
            "Ресурс",
            "Описание",
            "Дата",
            "Статус",
            "Причина отказа"
        ]
    }


@access_request_router.get(navigation.access_request.template.path, response_class=HTMLResponse)
async def access_request(
        request: Request,
        user: str = Depends(require_user),
):
    form_ctx = await get_form_context(user)
    return templates.TemplateResponse(
        "access_request.html",
        {
            "request": request,
            "user": user,
            **form_ctx
        }
    )


@access_request_router.post(navigation.access_request.form.path)
async def make_request(
        request: Request,
        resource_id: int,
        user: str = Depends(require_user),
):
    form = dict(await request.form())
    async with WEB_SESSION_FACTORY() as session:
        user_instance = await get_user_by_username(session, user)
        user_id = user_instance.inc
        await create(session, WebAccessRequestModel(
            user_inc=user_id,
            resource_id=resource_id,
            request_description=form["request_description"],
            status="Не рассмотрено"
        ))

    return RedirectResponse(f"/web/access_request", status_code=303)
