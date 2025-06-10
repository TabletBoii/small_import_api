from fastapi import APIRouter

from callers.import_generic import build_body_list_dependency
from controllers.budget.budget_upload import UploadBudgetData
from controllers.budget.upload_budget_currency_data import UploadBudgetCurrencyData
from controllers.budget.upload_budget_plan import UploadBudgetPlanData
from decorators.response import unified_response
from pydantic_models.request_models import BudgetCurrencyModel, BudgetPlanModel, BudgetValuesModel, PlanValuesModel

from fastapi import Depends

from controllers.budget.upload_plan import UploadPlanData
from database.sessions import PLAN_SESSION_FACTORY
from utils.utils import get_api_key

router = APIRouter(
    dependencies=[Depends(get_api_key)]
)


@router.post('/upload_plan_values')
@unified_response
async def upload_plan_values(
    cls_factory: UploadPlanData = Depends(
        build_body_list_dependency(
            param_name="plan_data",
            body_model=PlanValuesModel,
            constructor_cls=UploadPlanData
        )()
    )
):
    async with cls_factory as instance:
        instance.set_session(session_factory=PLAN_SESSION_FACTORY)
        await instance.run()
        return "Uploaded"


@router.post('/upload_budget_values')
@unified_response
async def upload_budget_values(
    cls_factory: UploadBudgetData = Depends(
        build_body_list_dependency(
            param_name="budget_data",
            body_model=BudgetValuesModel,
            constructor_cls=UploadBudgetData
        )()
    )
):
    async with cls_factory as instance:
        instance.set_session(session_factory=PLAN_SESSION_FACTORY)
        await instance.run()
        return "Uploaded"


@router.post('/upload_budget_currency')
@unified_response
async def upload_budget_currency_values(
    cls_factory: UploadBudgetCurrencyData = Depends(
        build_body_list_dependency(
            param_name="currency_data",
            body_model=BudgetCurrencyModel,
            constructor_cls=UploadBudgetCurrencyData
        )()
    )
):
    async with cls_factory as instance:
        instance.set_session(session_factory=PLAN_SESSION_FACTORY)
        await instance.run()
        return "Uploaded"


@router.post('/upload_budget_plan_values')
@unified_response
async def upload_budget_plan_values(
    cls_factory: UploadBudgetPlanData = Depends(
        build_body_list_dependency(
            param_name="plan_data",
            body_model=BudgetPlanModel,
            constructor_cls=UploadBudgetPlanData
        )()
    )
):
    async with cls_factory as instance:
        instance.set_session(session_factory=PLAN_SESSION_FACTORY)
        await instance.run()
        return "Uploaded"

