from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.samo.partner_model import Partner


async def get_partner_name_offset(
    session: AsyncSession,
    query: str,
    offset: int,
    limit: int
):
    stmt = select(Partner).where(Partner.name.ilike(f"{query}%")).order_by(Partner.inc).offset(offset).limit(limit)
    result = await session.execute(stmt)
    items = result.scalars().all()

    return items
