from typing import List

from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.sqlalchemy_v2.department import Department


async def get(session: AsyncSession) -> Sequence[Department]:
    stmt = select(Department)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_departments_by_name(session: AsyncSession, department_name_list: List[str]):
    stmt = select(Department.inc).where(Department.name.in_(department_name_list))
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_department_name_by_id(session: AsyncSession, department_id: int):
    stmt = select(Department.name).where(Department.inc == department_id)
    result = await session.execute(stmt)
    return result.scalars().first()
