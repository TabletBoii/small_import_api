import asyncio

from utils.agg_import import AggImport


async def get_agg_import(year_from: str) -> AggImport:

    agg_import_instance = AggImport(year_from=year_from)
    try:
        yield agg_import_instance
    except asyncio.CancelledError:
        await agg_import_instance.dispose_engine()
        raise "Cancelling request due to disconnect"
    finally:
        await agg_import_instance.dispose_engine()
