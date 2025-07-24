from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.samo.country_model import CountryModel


async def get_country_name_offset(
    session: AsyncSession,
    query: str,
    offset: int,
    limit: int
):
    stmt = select(CountryModel).where(CountryModel.name.ilike(f"{query}%")).order_by(CountryModel.inc).offset(offset).limit(limit)
    result = await session.execute(stmt)
    items = result.scalars().all()

    return items
