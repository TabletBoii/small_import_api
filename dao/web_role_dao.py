from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dao.web_dao import get_user_by_username
from models.sqlalchemy_v2.web import WebResource, WebResourceAccess, WebUser


async def get_user_permissions(session: AsyncSession, user: str):
    result = await session.execute(
        select(WebUser).where(WebUser.name == user)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise ValueError(f"User {user!r} not found")

    stmt = (
        select(
            WebResource.name.label("resource_name"),
            WebResourceAccess.has_access,
            WebResource.type.label("resource_type"),
            WebResource.name_cirill.label("name_cirill"),
            WebResource.description.label("description"),
        )
        .join(
            WebResource,
            WebResource.inc == WebResourceAccess.web_resource_inc
        )
        .where(WebResourceAccess.user_inc == user.inc)
    )

    rows = await session.execute(stmt)
    return [
        {"resource": name, "has_access": has_access, "resource_type": resource_type, "name_cirill": name_cirill, "description": description}
        for name, has_access, resource_type, name_cirill, description in rows.all()
    ]
