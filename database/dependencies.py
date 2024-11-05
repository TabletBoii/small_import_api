from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from database.sessions import KOMPAS_SESSION, PLAN_SESSION


async def get_kompas_db() -> AsyncGenerator[AsyncSession, None]:
    async with KOMPAS_SESSION() as session:
        yield session


async def get_plan_db() -> AsyncGenerator[AsyncSession, None]:
    async with PLAN_SESSION() as session:
        yield session
