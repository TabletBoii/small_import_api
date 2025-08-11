from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.web.web_access_request_model import WebAccessRequestModel
from models.web.web_resource_access_model import WebResourceAccessModel
from models.web.web_resource_model import WebResourceModel
from models.web.web_user_model import WebUserModel


async def create(session: AsyncSession, access_request: WebAccessRequestModel):
    session.add(access_request)
    await session.commit()


async def access_requests_by_username(session: AsyncSession, username: str):
    stmt = (select(
        WebAccessRequestModel.inc,
        WebResourceModel.name_cirill,
        WebAccessRequestModel.request_description,
        WebAccessRequestModel.request_date,
        WebAccessRequestModel.status,
        WebAccessRequestModel.rejection_reason
    ).join(
        WebUserModel,
        WebUserModel.inc == WebAccessRequestModel.user_inc
    ).join(
        WebResourceModel,
        WebResourceModel.inc == WebAccessRequestModel.resource_id
    ).where(WebUserModel.name == username))
    result = await session.execute(stmt)
    return result.mappings().all()


async def get_all(session: AsyncSession):
    stmt = (select(
        WebAccessRequestModel.inc,
        WebResourceModel.name_cirill,
        WebAccessRequestModel.request_description,
        WebAccessRequestModel.request_date,
        WebAccessRequestModel.status,
        WebAccessRequestModel.rejection_reason
    ).join(
        WebUserModel,
        WebUserModel.inc == WebAccessRequestModel.user_inc
    ).join(
        WebResourceModel,
        WebResourceModel.inc == WebAccessRequestModel.resource_id
    ))
    result = await session.execute(stmt)
    return result.all()


async def get_pending_requests(session: AsyncSession):
    stmt = (select(
        WebAccessRequestModel.inc,
        WebUserModel.name,
        WebResourceModel.name_cirill,
        WebAccessRequestModel.request_description,
        WebAccessRequestModel.request_date
    ).join(
        WebUserModel,
        WebUserModel.inc == WebAccessRequestModel.user_inc
    ).join(
        WebResourceModel,
        WebResourceModel.inc == WebAccessRequestModel.resource_id
    ).where(WebAccessRequestModel.status == "Не рассмотрено"))
    result = await session.execute(stmt)
    return result.mappings().all()


async def get_access_item_by_access_request(session: AsyncSession, request_id: int):
    stmt = (
        select(WebAccessRequestModel).where(WebAccessRequestModel.inc == request_id)
    )
    access_request_item = await session.execute(stmt)
    access_request_item = access_request_item.scalar()
    stmt = (
        select(WebResourceAccessModel)
        .where(WebResourceAccessModel.user_inc == access_request_item.user_inc)
        .where(WebResourceAccessModel.web_resource_inc == access_request_item.resource_id)
    )

    access_resource_item = await session.execute(stmt)
    access_resource_item = access_resource_item.scalar()
    return access_resource_item


async def request_rejection(session: AsyncSession, request_id: int, rejection_reason: str):
    stmt = update(WebAccessRequestModel).where(WebAccessRequestModel.inc == request_id).values(
        status="Отклонено",
        rejection_reason=rejection_reason
    )
    await session.execute(stmt)
    await session.commit()


async def request_confirmation(session: AsyncSession, request_id: int):
    access_resource_item = await get_access_item_by_access_request(session, request_id)
    if access_resource_item:
        await session.execute(
            update(WebAccessRequestModel).where(WebAccessRequestModel.inc == request_id).values(
                status="Подтверждено"
            )
        )
        update_access_resource_stmt = (
            update(WebResourceAccessModel)
            .where(WebResourceAccessModel.id == access_resource_item.id)
            .values(has_access=True)
        )
        await session.execute(update_access_resource_stmt)
        await session.commit()
        return
    update_stmt = update(WebAccessRequestModel).where(WebAccessRequestModel.inc == request_id).values(
        status="Подтверждено"
    ).returning(WebAccessRequestModel)
    result = await session.execute(update_stmt)
    updated_obj = result.scalar()
    insert_stmt = insert(WebResourceAccessModel).values(
        user_inc=updated_obj.user_inc,
        web_resource_inc=updated_obj.resource_id,
        has_access=True
    )
    await session.execute(insert_stmt)
    await session.commit()
