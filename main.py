import sys
import env_setup

from routers import budget, plan, default, office

from fastapi import FastAPI
from database.sessions import KOMPAS_ENGINE, PLAN_ENGINE

sys.stdout.reconfigure(encoding='utf-8')

app = FastAPI()

app.include_router(budget.router)
app.include_router(plan.router)
app.include_router(default.router)
app.include_router(office.router)

# app.add_middleware(RequestCancelledMiddleware)


@app.on_event("shutdown")
async def shutdown_event():
    print("Application closes")
    await KOMPAS_ENGINE.dispose()
    await PLAN_ENGINE.dispose()
