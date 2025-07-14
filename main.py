import os
import sys
import yaml
import uvicorn
import env_setup

import logging.config

from starlette.middleware import Middleware

from starlette.staticfiles import StaticFiles

from routers.api_router import api_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.sessions import KOMPAS_ENGINE, PLAN_ENGINE
from sub_app.admin_app import admin_app
from sub_app.web_app import web_app

sys.stdout.reconfigure(encoding='utf-8')

env_status = os.getenv("APP_ENV", "dev")
logging_path = f"logging.{env_status}.yaml"

if env_status != "dev":
    with open(logging_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)

middleware_list = [
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
app.mount("/admin", admin_app)
app.mount("/web", web_app)

app.include_router(api_router)


@app.on_event("shutdown")
async def shutdown_event():
    print("Application closes")
    await KOMPAS_ENGINE.dispose()
    await PLAN_ENGINE.dispose()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# TODO: Создать admin панель
# TODO: Добавить в web загрузку при обработке отчета, справочника т.д.

