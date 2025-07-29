from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from middlewares.webauth_middleware import WebAuthMiddleware
from routers.web_router.web import web_jinja_router
from utils.user_session_store import UserSessionStore
from utils.utils import get_data


web_middleware_list = [
    Middleware(
        SessionMiddleware,
        secret_key=get_data("WEB_SECRET_KEY"),
        session_cookie="web_session",
        max_age=int(get_data("WEB_SESSION_MAX_AGE"))
    ),
    Middleware(WebAuthMiddleware),
]

web_app = FastAPI(middleware=web_middleware_list)

web_app.state.session_store = UserSessionStore(folder="sessions")

web_app.include_router(
    web_jinja_router
)
