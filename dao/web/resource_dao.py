from sqlalchemy import select, update, delete, literal
from sqlalchemy.ext.asyncio import AsyncSession

from models.web.web_resource_access_model import WebResourceAccessModel
from models.web.web_resource_model import WebResourceModel
from models.web.web_resource_type_model import WebResourceTypeModel
from models.web.web_user_model import WebUserModel


async def get_web_resource_by_name(session: AsyncSession, web_resource_name: str):
    stmt = select(WebResourceModel).where(WebResourceModel.name == web_resource_name)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_resource_list(session: AsyncSession, get_cyrillic_type=None):
    stmt = (
        select(
            WebResourceModel.inc,
            WebResourceModel.name,
            WebResourceTypeModel.name.label("type") if get_cyrillic_type is None else WebResourceTypeModel.name_cirill.label("type"),
            WebResourceModel.name_cirill,
            WebResourceModel.description,
        )
        .join(
            WebResourceTypeModel,
            WebResourceTypeModel.inc == WebResourceModel.type
        )
    )
    result = await session.execute(stmt)
    return result.all()


async def get_resource_list_with_user_access(session: AsyncSession, username: str):
    stmt = (
        select(
            WebResourceModel.inc,
            WebResourceModel.name,
            WebResourceTypeModel.name_cirill.label("type"),
            WebResourceModel.name_cirill,
            WebResourceModel.description,
            WebResourceAccessModel.has_access,
        )
        .join(
            WebResourceTypeModel,
            WebResourceTypeModel.inc == WebResourceModel.type,
            isouter=True
        )
        .join(
            WebUserModel,
            literal(True),
            isouter=False
        )
        .join(
            WebResourceAccessModel,
            (WebResourceAccessModel.web_resource_inc == WebResourceModel.inc) &
            (WebResourceAccessModel.user_inc == WebUserModel.inc),
            isouter=True
        )
        .where(WebUserModel.name == username)
    )
    result = await session.execute(stmt)
    return result.all()


async def get_resource_type_list(session: AsyncSession):
    stmt = select(WebResourceTypeModel)
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_resource_by_inc(session: AsyncSession, resource_model: WebResourceModel) -> None:
    stmt = (
        update(WebResourceModel)
        .where(WebResourceModel.inc == resource_model.inc)
        .values(
            name=resource_model.name,
            type=resource_model.type,
            name_cirill=resource_model.name_cirill,
            description=resource_model.description
        )
    )
    await session.execute(stmt)
    await session.commit()


async def delete_resource(session: AsyncSession, resource_id: int):
    stmt = delete(WebResourceModel).where(WebResourceModel.inc == resource_id)
    await session.execute(stmt)
    await session.commit()


async def update_resource_type_by_inc(session: AsyncSession, resource_type_model: WebResourceTypeModel) -> None:
    stmt = (
        update(WebResourceTypeModel)
        .where(WebResourceTypeModel.inc == resource_type_model.inc)
        .values(
            name=resource_type_model.name
        )
    )
    await session.execute(stmt)
    await session.commit()


async def delete_resource_type(session: AsyncSession, resource_type_id: int):
    stmt = delete(WebResourceTypeModel).where(WebResourceTypeModel.inc == resource_type_id)
    await session.execute(stmt)
    await session.commit()
