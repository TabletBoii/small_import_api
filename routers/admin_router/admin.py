from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy import text, select
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from models.web.web_resource_model import WebResourceModel
from models.web.web_resource_type_model import WebResourceTypeModel
from models.web.web_user_model import WebUserModel
from .general_router_generator import generate_crud_router
from ..templates import admin_templates

admin_jinja_router = APIRouter()


resource_type_router = generate_crud_router(
    model=WebResourceTypeModel,
    url_prefix="/resource_type",
    table_headers=["ID", "Название"],
    model_name="resource_type",
    model_header_names=[
        "inc",
        "name"
    ],
    get_custom_query=select(
        WebResourceTypeModel.inc,
        WebResourceTypeModel.name
    ),
)
user_router = generate_crud_router(
    model=WebUserModel,
    url_prefix="/users",
    table_headers=[
        "ID",
        "Username",
        "Microsoft ID",
        "Microsoft Email",
        "Описание"
    ],
    model_header_names=[
        "inc",
        "name",
        "microsoft_oid",
        "microsoft_email",
        "description"
    ],
    get_custom_query=select(
        WebUserModel.inc,
        WebUserModel.name,
        WebUserModel.microsoft_oid,
        WebUserModel.microsoft_email,
        WebUserModel.description
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

admin_jinja_router.include_router(resource_router)
admin_jinja_router.include_router(resource_type_router)
admin_jinja_router.include_router(user_router)


@admin_jinja_router.get("/")
async def home(
    request: Request
):
    return admin_templates.TemplateResponse(
        "admin.html",
        {"request": request}
    )

# Не удалять импорты - все маршруты идут от этих импортов
##################################
from . import admin_auth
##################################
