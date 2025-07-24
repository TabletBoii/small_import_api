from typing import Callable

from fastapi import Depends
from starlette import status
from starlette.exceptions import HTTPException

from dao.web.web_role_dao import get_user_permissions
from database.sessions import WEB_SESSION_FACTORY
from utils.utils import require_user


def make_route_permission_deps(route_name: str) -> Callable:
    async def route_permission_deps(
        user: str = Depends(require_user),
    ):
        async with WEB_SESSION_FACTORY() as session:
            perms = await get_user_permissions(session, user)
        allowed = any(
            perm["resource"] == route_name and perm["has_access"]
            for perm in perms
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Нет доступа к маршруту {route_name}"
            )

        return True

    return route_permission_deps
