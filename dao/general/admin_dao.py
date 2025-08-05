from typing import Type, List, Any, Sequence

from sqlalchemy import update, delete, select, Row, RowMapping, TextClause
from sqlalchemy.ext.asyncio import AsyncSession


async def get_all(session: AsyncSession, model: Type, custom_query = None) -> Sequence[
    Row[Any] | RowMapping | Any]:
    if custom_query is not None:
        stmt = custom_query
    else:
        stmt = select(model)
    result = await session.execute(stmt)
    return result.all()


async def delete_by_id(session: AsyncSession, model: Type, item_id: int):
    stmt = delete(model).where(model.inc == item_id)
    await session.execute(stmt)
    await session.commit()


async def update_by_id(session: AsyncSession, model: Type, item_id: int, data: dict):
    stmt = update(model).where(model.inc == item_id).values(**data)
    await session.execute(stmt)
    await session.commit()
