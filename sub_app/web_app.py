from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

from middlewares.webauth_middleware import WebAuthMiddleware
from routers.web_router.routers import build_web_router
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
    build_web_router()
)


@web_app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return RedirectResponse(url="/web/home", status_code=302)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
