from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.web.web_user_model import WebUserModel


async def get_user_list(session: AsyncSession):
    stmt = select(
        WebUserModel.inc,
        WebUserModel.name,
        WebUserModel.microsoft_oid,
        WebUserModel.microsoft_email,
        WebUserModel.description
    )
    result = await session.execute(stmt)
    return result.all()


async def create_user(session: AsyncSession, user: WebUserModel) -> None:
    session.add(user)
    await session.flush()
    await session.refresh(user)


async def get_user_by_username(session: AsyncSession, username: str) -> WebUserModel:
    stmt = select(WebUserModel).where(WebUserModel.name == username)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_user_by_id(session: AsyncSession, user_id: int) -> WebUserModel:
    stmt = select(WebUserModel).where(WebUserModel.inc == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def is_user_exists_by_microsoft_oid(session: AsyncSession, microsoft_oid: str) -> bool:
    stmt = select(WebUserModel).where(WebUserModel.microsoft_oid == microsoft_oid)

    result = await session.execute(stmt)
    user_instance = result.scalars().first()

    if user_instance:
        return True
    return False


async def update_by_inc(session: AsyncSession, user_model: WebUserModel) -> None:
    stmt = (
        update(WebUserModel)
        .where(WebUserModel.inc == user_model.inc)
        .values(
            name=user_model.name,
            description=user_model.description,
            microsoft_email=user_model.microsoft_email,
            microsoft_oid=user_model.microsoft_oid
        )
    )
    await session.execute(stmt)
    await session.commit()


async def delete_user(session: AsyncSession, user_id: int):
    stmt = delete(WebUserModel).where(WebUserModel.inc == user_id)
    await session.execute(stmt)
    await session.commit()
