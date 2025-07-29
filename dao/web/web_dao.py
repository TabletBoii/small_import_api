from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.web.web_resource_model import WebResourceModel
from models.web.web_user_model import WebUserModel


async def get_user_by_username(session: AsyncSession, username: str) -> WebUserModel:
    stmt = select(WebUserModel).where(WebUserModel.name == username)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_user_by_id(session: AsyncSession, user_id: int) -> WebUserModel:
    stmt = select(WebUserModel).where(WebUserModel.inc == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def is_user_exists_by_microsoft_oid(session: AsyncSession, microsoft_oid: str) -> bool:
    stmt = select(WebUserModel).where(WebUserModel.microsoft_oid == microsoft_oid)

    result = await session.execute(stmt)
    user_instance = result.scalars().first()

    if user_instance:
        return True
    return False


async def create_user(session: AsyncSession, user: WebUserModel) -> None:
    session.add(user)
    await session.flush()
    await session.refresh(user)


async def get_web_resource_by_name(session: AsyncSession, web_resource_name: str):
    stmt = select(WebResourceModel).where(WebResourceModel.name == web_resource_name)
    result = await session.execute(stmt)
    return result.scalars().first()



