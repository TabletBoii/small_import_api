from typing import List

from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.samo.department_model import DepartmentModel


async def get(session: AsyncSession) -> Sequence[DepartmentModel]:
    stmt = select(DepartmentModel)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_dict(session: AsyncSession) -> Sequence[DepartmentModel]:
    stmt = select(DepartmentModel)
    result = await session.execute(stmt)
    department_instance_list = result.scalars().all()
    return [department.to_dict() for department in department_instance_list]


async def get_departments_by_name(session: AsyncSession, department_name_list: List[str]):
    stmt = select(DepartmentModel.inc).where(DepartmentModel.name.in_(department_name_list))
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_department_name_by_id(session: AsyncSession, department_id: int):
    stmt = select(DepartmentModel.name).where(DepartmentModel.inc == department_id)
    result = await session.execute(stmt)
    return result.scalars().first()
