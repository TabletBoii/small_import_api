from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse


class AdminAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        path = request.url.path

        if path.startswith("/admin"):
            if path.startswith(("/admin/login", "/admin/logout", "/static", "/favicon.ico")):
                return await call_next(request)

            if not request.session.get("admin"):
                return RedirectResponse(url="/admin/login", status_code=302)

        return await call_next(request)
