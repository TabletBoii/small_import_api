from fastapi import APIRouter

from routers.web_router.routers.access_request import build_access_request_router
from routers.web_router.routers.auth import build_auth_router
from routers.web_router.routers.directories import build_directories_router
from routers.web_router.routers.download import build_download_router
from routers.web_router.routers.powerbi_reports import build_powerbi_reports_router
from routers.web_router.routers.reports import build_report_router
from routers.web_router.web_base import base_router


def build_web_router() -> APIRouter:
    router = base_router
    router.include_router(build_report_router())
    router.include_router(build_powerbi_reports_router())
    router.include_router(build_download_router())
    router.include_router(build_directories_router())
    router.include_router(build_auth_router())
    router.include_router(build_access_request_router())
    return router
