import sys

import uvicorn

import env_setup

from routers import budget, plan, default, office, avg_time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.sessions import KOMPAS_ENGINE, PLAN_ENGINE

sys.stdout.reconfigure(encoding='utf-8')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(budget.router)
app.include_router(plan.router)
app.include_router(default.router)
app.include_router(office.router)
app.include_router(avg_time.router)


# app.add_middleware(RequestCancelledMiddleware)

@app.on_event("shutdown")
async def shutdown_event():
    print("Application closes")
    await KOMPAS_ENGINE.dispose()
    await PLAN_ENGINE.dispose()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
