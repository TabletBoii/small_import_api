from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.web.web_resource_access_model import WebResourceAccessModel
from models.web.web_resource_model import WebResourceModel
from models.web.web_user_model import WebUserModel


async def get_user_permissions(session: AsyncSession, user: str):
    result = await session.execute(
        select(WebUserModel).where(WebUserModel.name == user)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise ValueError(f"User {user!r} not found")

    stmt = (
        select(
            WebResourceModel.name.label("resource_name"),
            WebResourceAccessModel.has_access,
            WebResourceModel.type.label("resource_type"),
            WebResourceModel.name_cirill.label("name_cirill"),
            WebResourceModel.description.label("description"),
        )
        .join(
            WebResourceModel,
            WebResourceModel.inc == WebResourceAccessModel.web_resource_inc
        )
        .where(WebResourceAccessModel.user_inc == user.inc)
    )

    rows = await session.execute(stmt)
    return [
        {"resource": name, "has_access": has_access, "resource_type": resource_type, "name_cirill": name_cirill, "description": description}
        for name, has_access, resource_type, name_cirill, description in rows.all()
    ]
