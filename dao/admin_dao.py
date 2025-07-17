from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.web import AdminAuth


async def get_admin_by_username(session: AsyncSession, username: str) -> AdminAuth:
    stmt = select(AdminAuth).where(AdminAuth.username == username)
    result = await session.execute(stmt)
    return result.scalars().first()


async def create_admin_user(session: AsyncSession, admin_user: AdminAuth):
    async with session.begin():
        session.add(admin_user)

    await session.refresh(admin_user)
