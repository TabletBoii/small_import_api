from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from dao.web.web_dao import get_user_by_username, get_web_resource_by_name
from models.web.web_download_list_model import WebDownloadListModel
from models.web.web_resource_model import WebResourceModel
from models.web.web_user_model import WebUserModel
from pydantic_models.web_models import DownloadItem


async def get_download_list_by_user(session: AsyncSession, user_id: int):
    stmt = select(WebDownloadListModel).where(WebDownloadListModel.user_id == user_id)

    result = await session.execute(stmt)

    return result.scalars().all()


async def get_download_list_by_username(session: AsyncSession, username: str):
    user_instance = await session.execute(
        select(WebUserModel).where(WebUserModel.name == username)
    )
    user_id = user_instance.scalars().first().inc

    stmt = select(WebDownloadListModel).where(WebDownloadListModel.user_id == user_id)

    result = await session.execute(stmt)

    return result.scalars().all()


async def get_pydantic_download_list_by_username(session: AsyncSession, username: str):
    user_instance = await session.execute(
        select(WebUserModel).where(WebUserModel.name == username)
    )
    user_id = user_instance.scalars().first().inc

    stmt = (
        select(
            WebDownloadListModel.id,
            WebResourceModel.name.label("resource_name"),
            WebDownloadListModel.created_date,
            WebDownloadListModel.in_process,
            WebDownloadListModel.has_error,
            WebDownloadListModel.is_downloaded,
            WebDownloadListModel.params,
            WebDownloadListModel.error_msg,
        )
        .join(
            WebResourceModel,
            WebDownloadListModel.resource_id == WebResourceModel.inc
        )
        .where(WebDownloadListModel.user_id == user_id)
        .order_by(WebDownloadListModel.created_date.desc())
    )

    result = await session.execute(stmt)
    rows = result.all()

    return [
        DownloadItem(**row._mapping)
        for row in rows
    ]


async def get_download_by_id(session: AsyncSession, download_id: int):
    download = await session.get(WebDownloadListModel, download_id)
    return download


async def add_download(session: AsyncSession, download: WebDownloadListModel) -> int:
    session.add(download)
    await session.flush()
    await session.commit()
    await session.refresh(download)
    return download.id


async def change_progress_on_done(session: AsyncSession, download_id: int, error_msg=None):
    download_instance = await session.get(WebDownloadListModel, download_id)
    if not download_instance:
        raise ValueError("Загрузка не найдена")
    download_instance.in_process = False
    if error_msg is not None:
        download_instance.has_error = True
        download_instance.error_msg = error_msg
    await session.commit()


async def get_download_id(session: AsyncSession, username: str, resource_name: str, file_path: str, params: str):
    user_instance = await get_user_by_username(session, username)
    user_id = user_instance.inc
    resource_instance = await get_web_resource_by_name(session, resource_name)
    resource_id = resource_instance.inc
    download_id = await add_download(session, WebDownloadListModel(
        user_id=user_id,
        resource_id=resource_id,
        file_path=file_path,
        in_process=True,
        has_error=False,
        is_downloaded=False,
        params=params
    ))

    return download_id
