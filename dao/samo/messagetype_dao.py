from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.samo.department_model import DepartmentModel
from models.samo.messagetype_model import MessageTypeModel


async def get(session: AsyncSession) -> Sequence[MessageTypeModel]:
    stmt = select(MessageTypeModel)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_with_department(session: AsyncSession) -> Sequence[MessageTypeModel]:
    stmt = (
        select(MessageTypeModel)
        .options(
            joinedload(MessageTypeModel.department_field)
            .load_only(DepartmentModel.name)
        )
        .order_by(MessageTypeModel.inc)
    )
    res = await session.execute(stmt)
    return res.scalars().all()
