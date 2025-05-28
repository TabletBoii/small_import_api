
from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.sqlalchemy_v2.department import Department


async def get(session: AsyncSession) -> Sequence[Department]:
    stmt = select(Department)
    result = await session.execute(stmt)
    return result.scalars().all()
