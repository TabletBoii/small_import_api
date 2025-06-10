from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.sqlalchemy_v2.web import WebUser


async def get_user_by_username(session: AsyncSession, username: str) -> WebUser:
    stmt = select(WebUser).where(WebUser.name == username)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_user_by_id(session: AsyncSession, user_id: int) -> WebUser:
    stmt = select(WebUser).where(WebUser.inc == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def create_user(session: AsyncSession, user: WebUser) -> None:
    async with session.begin():
        session.add(user)

    await session.refresh(user)
