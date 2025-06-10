from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse


class WebAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        path = request.url.path

        if path.startswith("/web"):
            if path.startswith(("/web/login", "/web/logout", "/static", "/favicon.ico")):
                return await call_next(request)

            if not request.session.get("user"):
                return RedirectResponse(url="/web/login", status_code=302)

        return await call_next(request)
