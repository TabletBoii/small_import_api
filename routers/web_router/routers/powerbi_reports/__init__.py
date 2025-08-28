from fastapi import APIRouter

from routers.web_router.routers.powerbi_reports.base import powerbi_router
from routers.web_router.routers.powerbi_reports.powerbi_base import pbi_router


def build_powerbi_reports_router() -> APIRouter:
    router = powerbi_router
    router.include_router(pbi_router)
    return router
