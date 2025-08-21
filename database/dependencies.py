from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from database.sessions import KOMPAS_SESSION_FACTORY, PLAN_SESSION_FACTORY, WEB_DEV_SESSION_FACTORY, WEB_SESSION_FACTORY


async def get_kompas_session() -> AsyncGenerator[AsyncSession, None]:
    async with KOMPAS_SESSION_FACTORY() as session:
        yield session


async def get_plan_session() -> AsyncGenerator[AsyncSession, None]:
    async with PLAN_SESSION_FACTORY() as session:
        yield session


async def get_web_dev_session() -> AsyncGenerator[AsyncSession, None]:
    async with WEB_DEV_SESSION_FACTORY() as session:
        yield session


async def get_web_session() -> AsyncGenerator[AsyncSession, None]:
    async with WEB_SESSION_FACTORY() as session:
        yield session
