from fastapi import APIRouter

from callers.import_generic import build_body_list_dependency
from controllers.office.claims_bonus_system import ClaimsBonusSystem
from controllers.office.claims_inbetween_uploader import ClaimsInBetweenUploader
from controllers.office.claims_status_refresh import ClaimStatusRefresh
from database.sessions import KOMPAS_SESSION_FACTORY
from decorators.response import unified_response
from pydantic_models.request_models import UpdateObOpModel, ClaimsBonusSystemModel
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


@router.post("/status_refresh_ob_op")
@unified_response
async def status_refresh_ob_op(
    cls_factory: ClaimStatusRefresh = Depends(
        build_body_list_dependency(
            param_name="",
            constructor_cls=ClaimStatusRefresh
        )()
    )
):
    async with cls_factory as instance:
        instance.set_session(session_factory=KOMPAS_SESSION_FACTORY)
        return await instance.run()


@router.post("/claims_bonus_system")
@unified_response
async def claims_bonus_system(
    cls_factory: ClaimsBonusSystem = Depends(
        build_body_list_dependency(
            param_name="bonus_system_conditions",
            body_model=ClaimsBonusSystemModel,
            constructor_cls=ClaimsBonusSystem
        )()
    )
):
    async with cls_factory as instance:
        instance.set_session(session_factory=KOMPAS_SESSION_FACTORY)
        return await instance.run()

