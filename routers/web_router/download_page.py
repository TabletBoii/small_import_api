import os
from typing import List

from fastapi import Depends
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, FileResponse

from dao.web.web_dao import get_user_by_username
from dao.web.web_download_list_dao import get_download_list_by_username, get_pydantic_download_list_by_username, \
    get_download_by_id
from database.sessions import WEB_SESSION_FACTORY
from pydantic_models.web_models import DownloadItem
from routers.web_router.web import web_jinja_router, templates
from utils.utils import require_user


@web_jinja_router.get("/download", response_class=HTMLResponse)
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


@web_jinja_router.get("/get_downloads", response_model=List[DownloadItem])
async def get_downloads(
    user: str = Depends(require_user),
):
    async with WEB_SESSION_FACTORY() as session:
        download_list = await get_pydantic_download_list_by_username(session, user)

    return download_list


@web_jinja_router.get("/download_report/{download_id}")
async def download_report(
    download_id: int,
    user: str = Depends(require_user),
):

    async with WEB_SESSION_FACTORY() as session:
        download_item = await get_download_by_id(session, download_id)
        user_instance = await get_user_by_username(session, user)
        download_item.is_downloaded = True
        await session.commit()
    if not download_item or download_item.user_id != user_instance.inc:
        raise HTTPException(404, "Не найдено")

    return FileResponse(
        download_item.file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(download_item.file_path),
    )
