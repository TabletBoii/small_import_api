import os
from typing import List

from fastapi import Depends, APIRouter
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, FileResponse

from dao.web.web_user_dao import get_user_by_username
from dao.web.download_list_dao import get_download_list_by_username, get_pydantic_download_list_by_username, \
    get_download_by_id
from database.sessions import WEB_SESSION_FACTORY
from pydantic_models.web_models import DownloadItem
from routers.web_router.navigator.navigator_base import Navigator
from routers.web_router.web_base import templates, navigation
from utils.utils import require_user


download_router = APIRouter(
    prefix=navigation.download.path,
    tags=["Загрузка"],
)


@download_router.get(navigation.download.download_template.path, response_class=HTMLResponse)
async def download(
    request: Request,
    user: str = Depends(require_user),
):
    return templates.TemplateResponse(
        "download_page.html",
        {
            "request": request,
            "user": user,
            "error": None,
        }
    )


@download_router.get(navigation.download.get_downloads.path, response_model=List[DownloadItem])
async def get_downloads(
    user: str = Depends(require_user),
):
    async with WEB_SESSION_FACTORY() as session:
        download_list = await get_pydantic_download_list_by_username(session, user)

    return download_list


@download_router.get(navigation.download.download_report.path)
async def download_report(
    download_id: int,
    user: str = Depends(require_user),
):

    async with WEB_SESSION_FACTORY() as session:
        download_item = await get_download_by_id(session, download_id)
        user_instance = await get_user_by_username(session, user)

        if not download_item or download_item.user_id != user_instance.inc:
            raise HTTPException(404, "Не найдено")

        download_item.is_downloaded = True
        await session.commit()
        file_path = download_item.file_path

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(download_item.file_path),
    )
