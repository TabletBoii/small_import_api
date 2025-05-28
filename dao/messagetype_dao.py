from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.sqlalchemy_v2.department import Department
from models.sqlalchemy_v2.messagetype import MessageType


async def get(session: AsyncSession) -> Sequence[MessageType]:
    stmt = select(MessageType)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_with_department(session: AsyncSession) -> Sequence[MessageType]:
    stmt = (
        select(MessageType)
        .options(
            joinedload(MessageType.department_field)
            .load_only(Department.name)
        )
        .order_by(MessageType.inc)
    )
    res = await session.execute(stmt)
    return res.scalars().all()
