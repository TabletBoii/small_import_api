import asyncio
from typing import Optional

from utils.agg_import import AggImport


async def get_agg_import(year_from: str, state_inc: Optional[str] = None) -> AggImport:

    agg_import_instance = AggImport(year_from=year_from, state_inc=state_inc)
    try:
        yield agg_import_instance
    except asyncio.CancelledError:
        await agg_import_instance.dispose_engine()
        raise "Cancelling request due to disconnect"
    finally:
        await agg_import_instance.dispose_engine()
