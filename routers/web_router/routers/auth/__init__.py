from fastapi import APIRouter

from routers.web_router.routers.auth.base import auth_router


def build_auth_router() -> APIRouter:
    return auth_router
