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


async def create_user(session: AsyncSession, user: WebUserModel) -> None:
    async with session.begin():
        session.add(user)

    await session.refresh(user)


async def get_web_resource_by_name(session: AsyncSession, web_resource_name: str):
    stmt = select(WebResourceModel).where(WebResourceModel.name == web_resource_name)
    result = await session.execute(stmt)
    return result.scalars().first()



