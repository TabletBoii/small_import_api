from typing import List, Tuple, Any, Sequence

from sqlalchemy import Sequence, select, Row
from sqlalchemy.ext.asyncio import AsyncSession

from models.sqlalchemy_v2.usnames import Usnames


async def get(session: AsyncSession) -> Sequence[Usnames]:
    stmt = select(Usnames).execution_options(caller="usnames.get")
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_id_by_similar_name(session: AsyncSession, name_pattern: str) -> Sequence[Usnames]:
    stmt = (
            select(Usnames.code)
            .where(Usnames.name.like(f"%{name_pattern}%"))
            .execution_options(caller="usnames.get_id_by_similar_name")
            )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_name_by_id_dict(session: AsyncSession, id_list: List[int]):
    stmt = (
        select(Usnames.code, Usnames.name)
        .where(Usnames.code.in_(id_list))
        .execution_options(caller="usnames.get_name_by_id_list")
    )
    result = await session.execute(stmt)
    return dict(result.all())
