from fastapi import APIRouter
from fastapi.responses import JSONResponse, UJSONResponse

from callers.import_generic import build_body_list_dependency
from controllers.claims_inbetween_uploader import ClaimsInBetweenUploader
from database.sessions import PLAN_SESSION_FACTORY, KOMPAS_SESSION_FACTORY
from decorators.response import unified_response
from pydantic_models.request_models import UpdateObOpModel
from utils.utils import get_api_key

from fastapi import Depends

router = APIRouter(
    dependencies=[Depends(get_api_key)]
)


@router.post("/update_ob_op")
@unified_response
async def update_ob_op(
    cls_factory: ClaimsInBetweenUploader = Depends(
        build_body_list_dependency(
            param_name="plan_data",
            body_model=UpdateObOpModel,
            constructor_cls=ClaimsInBetweenUploader
        )()
    )
):
    async with cls_factory as instance:
        instance.set_session(session_factory=KOMPAS_SESSION_FACTORY)
        return await instance.run()
