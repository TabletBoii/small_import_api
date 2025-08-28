from fastapi import APIRouter

from routers.web_router.routers.reports.avg_time_report import avg_time_report_router
from routers.web_router.routers.reports.base import reports_router
from routers.web_router.routers.reports.report_dmc import dmc_report_router


def build_report_router() -> APIRouter:
    router = reports_router
    router.include_router(dmc_report_router)
    router.include_router(avg_time_report_router)
    return router
