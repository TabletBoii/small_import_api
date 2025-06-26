import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from controllers.monitor.GetFullMonitorController import GetFullMonitor
from database.sessions import KOMPAS_SESSION_FACTORY
from decorators.response import unified_response
from pydantic_models.request_models import GetFullMonitorParams
from utils.utils import get_api_key

router = APIRouter(
    dependencies=[Depends(get_api_key)],
    prefix="/monitor"
)


@router.get("/get_full/")
@unified_response
async def get_full_monitor(
    query_items: Annotated[GetFullMonitorParams, Depends()]
):
    logging.info()
    cls_instance = GetFullMonitor(model=query_items)
    cls_instance.set_session(session_factory=KOMPAS_SESSION_FACTORY)
    result = await cls_instance.run()
    return result
