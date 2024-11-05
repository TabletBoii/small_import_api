import asyncio
from typing import Optional

from controllers.agg_import import AggImport
from controllers.partner_directory_import import PartnerDirectoryImport


async def get_agg_import(year_from: str, state_inc: Optional[str] = None) -> AggImport:

    agg_import_instance = AggImport(year_from=year_from, state_inc=state_inc)
    try:
        yield agg_import_instance
    except asyncio.CancelledError:
        await agg_import_instance.dispose_engine()
        raise "Cancelling request due to disconnect"
    finally:
        await agg_import_instance.dispose_engine()


async def get_partner_directory_import(state_inc: Optional[str] = None) -> PartnerDirectoryImport:
    partner_directory_import = PartnerDirectoryImport(state_inc=state_inc)
    try:
        yield partner_directory_import
    except asyncio.CancelledError:
        await partner_directory_import.dispose_engine()
        raise "Cancelling request due to disconnect"
    finally:
        await partner_directory_import.dispose_engine()
