import asyncio
from typing import Optional

from controllers.agg_import import AggImport
from controllers.partner_directory_import import PartnerDirectoryImport
from controllers.upload_plan import UploadPlanData
from pydantic_models.request_models import PlanValuesModel


async def get_agg_import_class(year_from: str, state_inc: Optional[str] = None) -> AggImport:

    agg_import_instance = AggImport(year_from=year_from, state_inc=state_inc)
    try:
        yield agg_import_instance
    except asyncio.CancelledError:
        await agg_import_instance.dispose_engine()
        raise "Cancelling request due to disconnect"
    finally:
        await agg_import_instance.dispose_engine()


async def get_partner_directory_import_class(state_inc: Optional[str] = None) -> PartnerDirectoryImport:
    partner_directory_import = PartnerDirectoryImport(state_inc=state_inc)
    try:
        yield partner_directory_import
    except asyncio.CancelledError:
        raise "Cancelling request due to disconnect"
    finally:
        print(f"{partner_directory_import} closed successfully")


async def get_upload_plan_class(plan_data: list[PlanValuesModel]) -> PartnerDirectoryImport:
    upload_plan_data = UploadPlanData(plan_data=plan_data)
    try:
        yield upload_plan_data
    except asyncio.CancelledError:
        raise "Cancelling request due to disconnect"
    finally:
        print(f"{upload_plan_data} closed successfully")
