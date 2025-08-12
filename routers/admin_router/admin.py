from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy import text, select, func
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from database.sessions import WEB_SESSION_FACTORY
from models.web.web_access_request_model import WebAccessRequestModel
from models.web.web_pbi_report_data_model import WebPbiReportDataModel
from models.web.web_resource_access_model import WebResourceAccessModel
from models.web.web_resource_model import WebResourceModel
from models.web.web_resource_type_model import WebResourceTypeModel
from models.web.web_user_model import WebUserModel
from .general_router_generator import generate_crud_router
from ..templates import admin_templates

admin_jinja_router = APIRouter()


resource_type_router = generate_crud_router(
    model=WebResourceTypeModel,
    url_prefix="/resource_type",
    table_headers=["ID", "Название", "Название(кир.)"],
    model_name="resource_type",
    model_header_names=[
        "inc",
        "name",
        "name_cirill"
    ],
    get_custom_query=select(
        WebResourceTypeModel.inc,
        WebResourceTypeModel.name,
        WebResourceTypeModel.name_cirill
    ),
)

pbi_resource_router = generate_crud_router(
    model=WebPbiReportDataModel,
    url_prefix="/pbi_resource",
    table_headers=["ID", "ID рабочей области", "ID отчета", "Ресурс"],
    model_name="pbi_resource",
    model_header_names=[
        "id",
        "workspace_id",
        "report_id",
        "resource_id"
    ],
    get_custom_query=select(
        WebPbiReportDataModel.id,
        WebPbiReportDataModel.workspace_id,
        WebPbiReportDataModel.report_id,
        WebResourceModel.name_cirill.label("resource_id")
    ).join(
            WebResourceModel,
            WebResourceModel.inc == WebPbiReportDataModel.resource_id
    ),
    dropdown_field_dict={
        "resource_id": [
            WebResourceModel,
            select(WebResourceModel.inc, WebResourceModel.name_cirill.label("name"))
        ]
    },
)

user_router = generate_crud_router(
    model=WebUserModel,
    url_prefix="/users",
    table_headers=[
        "ID",
        "Username",
        "Microsoft ID",
        "Microsoft Email",
        "Описание",
        "Активирован"
    ],
    model_header_names=[
        "inc",
        "name",
        "microsoft_oid",
        "microsoft_email",
        "description",
        "is_activated"
    ],
    get_custom_query=select(
        WebUserModel.inc,
        WebUserModel.name,
        WebUserModel.microsoft_oid,
        WebUserModel.microsoft_email,
        WebUserModel.description,
        WebUserModel.is_activated
    ),
    model_name="users"
)
resource_router = generate_crud_router(
    model=WebResourceModel,
    url_prefix="/resources",
    table_headers=[
        "ID",
        "Название",
        "Тип",
        "Название(кир.)",
        "Описание"
    ],
    model_header_names=[
        "inc",
        "name",
        "type",
        "name_cirill",
        "description"
    ],
    get_custom_query=(
        select(
            WebResourceModel.inc,
            WebResourceModel.name,
            WebResourceTypeModel.name.label("type"),
            WebResourceModel.name_cirill,
            WebResourceModel.description,
        )
        .join(
            WebResourceTypeModel,
            WebResourceTypeModel.inc == WebResourceModel.type
        )
    ),
    dropdown_field_dict={
        "type": [
            WebResourceTypeModel,
            select(WebResourceTypeModel.inc, WebResourceTypeModel.name)
        ]
    },
    model_name="resources"
)
access_router = generate_crud_router(
    model=WebResourceAccessModel,
    url_prefix="/access",
    table_headers=[
        "ID",
        "Пользователь",
        "Ресурс",
        "Доступ"
    ],
    model_header_names=[
        "inc",
        "user_inc",
        "web_resource_inc",
        "has_access"
    ],
    get_custom_query=(
        select(
            WebResourceAccessModel.id.label("inc"),
            WebUserModel.name.label("user_inc"),
            WebResourceModel.name.label("web_resource_inc"),
            WebResourceAccessModel.has_access
        )
        .join(
            WebUserModel,
            WebUserModel.inc == WebResourceAccessModel.user_inc
        ).join(
            WebResourceModel,
            WebResourceModel.inc == WebResourceAccessModel.web_resource_inc
        )
    ),
    dropdown_field_dict={
        "user_inc": [
            WebUserModel,
            select(WebUserModel.inc, WebUserModel.name)
        ],
        "web_resource_inc": [
            WebResourceModel,
            select(WebResourceModel.inc, WebResourceModel.name)
        ]
    },
    model_name="web_access"
)


admin_jinja_router.include_router(pbi_resource_router)
admin_jinja_router.include_router(resource_router)
admin_jinja_router.include_router(resource_type_router)
admin_jinja_router.include_router(user_router)
admin_jinja_router.include_router(access_router)

#
# async def home_page_ctx():


@admin_jinja_router.get("/")
async def home(
    request: Request
):
    return admin_templates.TemplateResponse(
        "admin.html",
        {
            "request": request
        }
    )


@admin_jinja_router.get("/pending_access_request_count")
async def get_pending_count():
    async with WEB_SESSION_FACTORY() as session:
        count = await session.scalar(
            select(func.count()).select_from(WebAccessRequestModel)
            .where(WebAccessRequestModel.status == "Не рассмотрено")
        )
        return {"count": count}


# Не удалять импорты - все маршруты идут от этих импортов
##################################
from . import admin_auth
from . import admin_access_request
##################################
