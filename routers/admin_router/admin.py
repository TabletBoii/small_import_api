from fastapi import APIRouter, Depends, FastAPI
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

admin_jinja_router = APIRouter()


@admin_jinja_router.get("/")
async def home(
    request: Request
):
    return templates.TemplateResponse(
        "admin/admin.html",
        {"request": request}
    )

from . import admin_auth
