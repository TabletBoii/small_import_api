from typing import Callable, Optional, Any

from fastapi import Depends
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request

from dao.web.role_dao import get_user_permissions
from database.sessions import WEB_SESSION_FACTORY
from utils.utils import require_user


# def make_route_permission_deps(route_name: str = None, report_name: str = None) -> Callable:
#     async def route_permission_deps(
#             user: str = Depends(require_user),
#     ):
#         resource_name = route_name if report_name is None else report_name
#         async with WEB_SESSION_FACTORY() as session:
#             perms = await get_user_permissions(session, user)
#         allowed = any(
#             perm["resource"] == resource_name and perm["has_access"]
#             for perm in perms
#         )
#         if not allowed:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Нет доступа к маршруту {resource_name}"
#             )
#
#         return True
#
#     return route_permission_deps


def make_route_permission_deps(
    resource_access_name: str
) -> Callable[..., Any]:

    async def route_permission_deps(
        request: Request,
        route_param: str = None,
        user: str = Depends(require_user),
    ):
        print(route_param)
        if route_param:
            resource = route_param
        else:
            resource = resource_access_name

        async with WEB_SESSION_FACTORY() as session:
            perms = await get_user_permissions(session, user)

        if not any(p["resource"] == resource and p["has_access"] for p in perms):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Нет доступа к ресурсу {resource}"
            )
        return True

    return route_permission_deps
