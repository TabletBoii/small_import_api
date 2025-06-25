from fastapi import APIRouter

from .api import budget, plan, office, default, monitor
from .web import user

api_router = APIRouter(prefix="/api")

api_router.include_router(budget.router)
api_router.include_router(plan.router)
api_router.include_router(default.router)
api_router.include_router(office.router)
api_router.include_router(user.router)
api_router.include_router(monitor.router)
