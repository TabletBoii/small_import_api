import os
import sys
import yaml
import uvicorn
from sqlalchemy import update

import env_setup

import logging.config

from starlette.middleware import Middleware

from starlette.staticfiles import StaticFiles

from models.web.web_download_list_model import WebDownloadListModel
from routers.api_router import api_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.sessions import KOMPAS_ENGINE, PLAN_ENGINE, WEB_SESSION_FACTORY
from sub_app.admin_app import admin_app
from sub_app.web_app import web_app

sys.stdout.reconfigure(encoding='utf-8')

env_status = os.getenv("APP_ENV", "dev")
logging_path = f"logging.{env_status}.yaml"


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


@app.on_event("startup")
async def mark_interrupted_downloads():
    async with WEB_SESSION_FACTORY() as session:  # AsyncSession
        # обновляем все, у которых in_process=True
        await session.execute(
            update(WebDownloadListModel)
            .where(WebDownloadListModel.in_process == True)
            .values(
                in_process=False,
                has_error=True,
                error_msg="Процесс прерван из‑за остановки сервера"
            )
        )
        await session.commit()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# TODO: Создать admin панель
# TODO: Добавить в web загрузку при обработке отчета, справочника т.д.
