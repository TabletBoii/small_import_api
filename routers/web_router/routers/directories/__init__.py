from fastapi import APIRouter

from routers.web_router.routers.directories.base import directories_router
from routers.web_router.routers.directories.claims import claims_router
from routers.web_router.routers.directories.departments import department_directory_router
from routers.web_router.routers.directories.direction import direction_router


def build_directories_router() -> APIRouter:
    router = directories_router
    router.include_router(claims_router)
    router.include_router(department_directory_router)
    router.include_router(direction_router)
    return router
