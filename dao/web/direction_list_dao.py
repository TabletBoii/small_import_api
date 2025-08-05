from typing import Sequence, List

from sqlalchemy import select, delete, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.web.web_direction_list_model import WebDirectionListModel
from pydantic_models.web_models import Direction


async def get_all(session: AsyncSession) -> Sequence[WebDirectionListModel]:
    stmt = select(WebDirectionListModel)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_all_without_id(session: AsyncSession) -> Sequence[WebDirectionListModel]:
    cols = [
        col
        for col in WebDirectionListModel.__table__.columns
        if col.name != "inc"
    ]

    stmt = select(*cols)
    result = await session.execute(stmt)
    return result.scalars().all()


async def delete_by_inc(session: AsyncSession, inc_list_to_delete) -> None:
    stmt = (
        delete(WebDirectionListModel)
        .where(
            WebDirectionListModel.inc.in_(inc_list_to_delete)
        )
    )
    await session.execute(stmt)
    await session.commit()


async def create(session: AsyncSession, list_to_create: List[Direction]) -> None:
    rows = []
    for d in list_to_create:
        rows.append({
            "airline_name":             d.airline_name,
            "country_of_departure":     d.country_of_departure,
            "country_of_arrival":       d.country_of_arrival,
            "town_of_departure":        d.town_of_departure,
            "town_of_arrival":          d.town_of_arrival,
            "town_of_departure_alias":  d.town_of_departure_alias,
            "town_of_arrival_alias":    d.town_of_arrival_alias,
            "airline_alias":            d.airline_alias,
            "status":                   d.status,
            "flight_alias":             d.flight_alias,
        })
    stmt = insert(WebDirectionListModel)
    await session.execute(stmt, rows)
    await session.commit()


async def update_by_inc(session: AsyncSession, inc_list_to_update: List[Direction]) -> None:
    for row in inc_list_to_update:
        stmt = (
            update(WebDirectionListModel)
            .where(WebDirectionListModel.inc == row.inc)
            .values(
                airline_name=row.airline_name,
                country_of_departure=row.country_of_departure,
                country_of_arrival=row.country_of_arrival,
                town_of_departure=row.town_of_departure,
                town_of_arrival=row.town_of_arrival,
                town_of_departure_alias=row.town_of_departure_alias,
                town_of_arrival_alias=row.town_of_arrival_alias,
                airline_alias=row.airline_alias,
                status=row.status,
                flight_alias=row.flight_alias
            )
        )
        await session.execute(stmt)
    await session.commit()


async def create_or_update(session: AsyncSession, new_rows) -> None:
    stmt = insert(WebDirectionListModel)
    await session.execute(stmt, new_rows)
    await session.commit()
