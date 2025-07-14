from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from middlewares.adminauth_middleware import AdminAuthMiddleware
from routers.admin_router.admin import admin_jinja_router
from utils.utils import get_data


admin_middleware_list = [
    Middleware(
        SessionMiddleware,
        secret_key=get_data("WEB_SECRET_KEY"),
        session_cookie="admin_session",
        max_age=int(get_data("WEB_SESSION_MAX_AGE"))
    ),
    Middleware(AdminAuthMiddleware),
]

admin_app = FastAPI(middleware=admin_middleware_list)

admin_app.include_router(
    admin_jinja_router
)
