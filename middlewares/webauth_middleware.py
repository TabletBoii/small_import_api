import time
from datetime import datetime, timedelta

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse

from sub_app.msal_app import msal_app
from utils.msal_scopes import AUTH_SCOPE


class WebAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        path = request.url.path
        session_store = request.app.state.session_store
        session_data = request.session
        session_id = request.cookies.get("session_id")
        if path.startswith("/web"):
            if path.startswith(("/web/login", "/web/logout", "/static", "/favicon.ico")):
                return await call_next(request)

            if session_id:
                msal_session_data = session_store.read(session_id)
                now = time.time()
                if not request.session.get("user"):
                    request.session["user"] = msal_session_data["email"]
                if msal_session_data["expires_at"] < now:
                    new_session_data = msal_app.acquire_token_by_refresh_token(
                        msal_session_data["refresh_token"],
                        scopes=[*AUTH_SCOPE]
                    )
                    new_access = new_session_data["access_token"]
                    new_refresh = new_session_data.get("refresh_token", msal_session_data["refresh_token"])
                    new_expires = now + int(new_session_data.get("expires_in", 0))

                    session_store.update(
                        session_id,
                        access_token=new_access,
                        refresh_token=new_refresh,
                        expires_at=new_expires,
                    )
                    session_data["expires_at"] = new_expires
                    response = await call_next(request)
                    expires = (datetime.now() + timedelta(days=7))
                    response.set_cookie(
                        key="session_id",
                        value=session_id,
                        httponly=True,
                        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                        path="/"
                    )
                    return response

            if not request.session.get("user"):
                return RedirectResponse(url="/web/login", status_code=302)

        return await call_next(request)
