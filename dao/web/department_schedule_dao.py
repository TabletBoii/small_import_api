from typing import Sequence, Iterable

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from models.web.department_schedule_model import DepartmentScheduleModel


async def get_department_schedule(session: AsyncSession) -> Sequence[dict]:
    stmt = select(DepartmentScheduleModel)
    result = await session.execute(stmt)
    department_schedule_instance_list = result.scalars().all()
    return [department.to_dict() for department in department_schedule_instance_list]


async def get_distinct_department_inc(session: AsyncSession):
    stmt = select(DepartmentScheduleModel.department_inc.distinct())
    result = await session.execute(stmt)
    return result.scalars().all()


async def insert_all(session: AsyncSession, department_schedule_data: list[DepartmentScheduleModel]):
    session.add_all(department_schedule_data)
    await session.commit()


async def merge_department_schedule(
    session: AsyncSession,
    items: Iterable["DepartmentScheduleModel"],
) -> None:
    rows = [{
        "department_inc": item.department_inc,
        "week_day":       item.week_day,
        "start_time":     item.start_time,
        "end_time":       item.end_time,
    } for item in items]

    if not rows:
        return

    async with session.begin():
        await session.execute(text("""
IF OBJECT_ID('tempdb..#Src') IS NOT NULL DROP TABLE #Src;
CREATE TABLE #Src(
  department_inc INT NOT NULL,
  week_day       NVARCHAR(30) NOT NULL,
  start_time     TIME NULL,
  end_time       TIME NULL
);
        """))
        await session.execute(
            text("INSERT INTO #Src(department_inc, week_day, start_time, end_time) "
                 "VALUES (:department_inc, :week_day, :start_time, :end_time)"),
            rows,
        )

        await session.execute(text("""
MERGE dbo.department_schedule WITH (HOLDLOCK) AS t
USING #Src AS s
  ON  t.department_inc = s.department_inc
  AND t.week_day       = s.week_day

WHEN MATCHED
     AND (s.start_time IS NULL OR s.end_time IS NULL)
THEN
  DELETE

WHEN MATCHED
     AND s.start_time IS NOT NULL
     AND s.end_time   IS NOT NULL
THEN
  UPDATE SET t.start_time = s.start_time,
             t.end_time   = s.end_time

WHEN NOT MATCHED BY TARGET
     AND s.start_time IS NOT NULL
     AND s.end_time   IS NOT NULL
THEN
  INSERT (department_inc, week_day, start_time, end_time)
  VALUES (s.department_inc, s.week_day, s.start_time, s.end_time)

WHEN NOT MATCHED BY SOURCE
THEN
  DELETE;
        """))
        await session.execute(text("DROP TABLE #Src;"))
