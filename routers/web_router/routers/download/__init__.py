from fastapi import APIRouter

from routers.web_router.routers.download.base import download_router


def build_download_router() -> APIRouter:
    return download_router
