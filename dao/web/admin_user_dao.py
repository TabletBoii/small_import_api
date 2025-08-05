from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.web.admin_user_model import AdminAuth


async def get_admin_by_username(session: AsyncSession, username: str) -> AdminAuth:
    stmt = select(AdminAuth).where(AdminAuth.username == username)
    result = await session.execute(stmt)
    return result.scalars().first()


async def create_admin_user(session: AsyncSession, admin_user: AdminAuth):
    session.add(admin_user)
    await session.flush()
    await session.refresh(admin_user)
    await session.commit()
