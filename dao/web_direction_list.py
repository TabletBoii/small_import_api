from typing import Sequence

from sqlalchemy import select, delete, and_, cast, VARCHAR, insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.sqlalchemy_v2.web import WebDirectionList


async def get_all(session: AsyncSession) -> Sequence[WebDirectionList]:
    stmt = select(WebDirectionList)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_all_without_id(session: AsyncSession) -> Sequence[WebDirectionList]:
    cols = [
        col
        for col in WebDirectionList.__table__.columns
        if col.name != "inc"
    ]

    stmt = select(*cols)
    result = await session.execute(stmt)
    return result.scalars().all()


async def delete_by_direction(session: AsyncSession, list_to_delete) -> None:
    for dep_alias, arr_alias, air_alias, status, flight in list_to_delete:
        stmt = (
            delete(WebDirectionList)
            .where(
                and_(
                    cast(WebDirectionList.town_of_departure_alias, VARCHAR(length=8000)) == dep_alias,
                    cast(WebDirectionList.town_of_arrival_alias, VARCHAR(length=8000)) == arr_alias,
                    cast(WebDirectionList.airline_alias, VARCHAR(length=8000)) == air_alias,
                    cast(WebDirectionList.status, VARCHAR(length=8000)) == status,
                    cast(WebDirectionList.flight_alias, VARCHAR(length=8000)) == flight,
                )
            )
        )
        await session.execute(stmt)
    await session.commit()


async def create_or_update(session: AsyncSession, new_rows) -> None:
    stmt = insert(WebDirectionList)
    await session.execute(stmt, new_rows)
    await session.commit()
