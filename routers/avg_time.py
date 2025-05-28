from fastapi import APIRouter, Depends, status

from callers.import_generic import build_body_list_dependency
from controllers.avg_time_report import AvgTimeReport
from database.sessions import KOMPAS_SESSION_FACTORY
from pydantic_models.request_models import AvgTimeReportModel
from pydantic_models.response_models import GenericResponse
from utils.utils import get_api_key

router = APIRouter(
    dependencies=[Depends(get_api_key)],
    prefix="/avg_time",
    tags=["avg_time"]
)


@router.post("/")
async def get_avg_time_report(
    cls_factory: AvgTimeReport = Depends(
        build_body_list_dependency(
            param_name="plan_data",
            body_model=AvgTimeReportModel,
            constructor_cls=AvgTimeReport
        )()
    )
):
    async with cls_factory as instance:
        instance.set_session(session_factory=KOMPAS_SESSION_FACTORY)
        response_data = await instance.run()
        return GenericResponse(data=response_data)
