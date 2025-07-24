from typing import List

from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.samo.usnames_model import UsnamesModel


async def get(session: AsyncSession) -> Sequence[UsnamesModel]:
    stmt = select(UsnamesModel).execution_options(caller="usnames.get")
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_id_by_similar_name(session: AsyncSession, name_pattern: str) -> Sequence[UsnamesModel]:
    stmt = (
            select(UsnamesModel.code)
            .where(UsnamesModel.name.like(f"%{name_pattern}%"))
            .execution_options(caller="usnames.get_id_by_similar_name")
            )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_name_by_id_dict(session: AsyncSession, id_list: List[int]):
    stmt = (
        select(UsnamesModel.code, UsnamesModel.name)
        .where(UsnamesModel.code.in_(id_list))
        .execution_options(caller="usnames.get_name_by_id_list")
    )
    result = await session.execute(stmt)
    return dict(result.all())
