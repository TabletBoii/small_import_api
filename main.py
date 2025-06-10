import os
import sys

import env_setup

import uvicorn
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from starlette.staticfiles import StaticFiles
from middlewares.webauth_middleware import WebAuthMiddleware

from routers.api_router import api_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.sessions import KOMPAS_ENGINE, PLAN_ENGINE
from routers.web_router import web
from utils.utils import get_data

sys.stdout.reconfigure(encoding='utf-8')

middleware_list = [
    Middleware(
        SessionMiddleware,
        secret_key=get_data("WEB_SECRET_KEY"),
        max_age=int(get_data("WEB_SESSION_MAX_AGE"))
    ),
    Middleware(WebAuthMiddleware),
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = FastAPI(middleware=middleware_list)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router)
app.include_router(web.jinja_router)


@app.on_event("shutdown")
async def shutdown_event():
    print("Application closes")
    await KOMPAS_ENGINE.dispose()
    await PLAN_ENGINE.dispose()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
