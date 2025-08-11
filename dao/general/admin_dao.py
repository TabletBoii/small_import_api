from typing import Type, List, Any, Sequence

from sqlalchemy import update, delete, select, Row, RowMapping, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.pickleable import User

from models.base import Base


async def get_all(session: AsyncSession, model: Type, custom_query = None) -> Sequence[
    Row[Any] | RowMapping | Any]:
    if custom_query is not None:
        stmt = custom_query
    else:
        stmt = select(model)
    result = await session.execute(stmt)
    return result.all()


async def delete_by_id(session: AsyncSession, model: Type, item_id: int):
    if 'inc' in model.__table__.columns:
        stmt = delete(model).where(model.inc == item_id)
    else:
        stmt = delete(model).where(model.id == item_id)

    await session.execute(stmt)
    await session.commit()


async def update_by_id(session: AsyncSession, model: Type, item_id: int, data: dict):
    if 'inc' in model.__table__.columns:
        stmt = update(model).where(model.inc == item_id).values(**data)
    else:
        stmt = update(model).where(model.id == item_id).values(**data)
    await session.execute(stmt)
    await session.commit()


async def create(session: AsyncSession, model: Base):
    session.add(model)
    await session.commit()
