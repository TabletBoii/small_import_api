from fastapi import APIRouter

from routers.web_router.routers.access_request.base import access_request_router


def build_access_request_router() -> APIRouter:
    return access_request_router
