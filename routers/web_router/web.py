
from fastapi import Request, Depends, APIRouter
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from utils.utils import require_user

templates = Jinja2Templates(directory="templates")

jinja_router = APIRouter(
    prefix="/web",
    tags=["web"]
)


@jinja_router.get("/")
async def home(request: Request, user: str = Depends(require_user)):
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "user": user}
    )


@jinja_router.get("/reports", response_class=HTMLResponse)
async def reports(request: Request, user: str = Depends(require_user)):
    return templates.TemplateResponse("reports.html", {"request": request, "user": user})


@jinja_router.get("/directories", response_class=HTMLResponse)
async def directories(request: Request, user: str = Depends(require_user)):
    return templates.TemplateResponse("directories.html", {"request": request, "user": user})


from .reports import avg_time_report
from .directories import claims
from . import auth

