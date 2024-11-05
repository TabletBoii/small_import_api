import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from controllers.partner_directory_import import PartnerDirectoryImport


class PartnerDirectoryImportDependency:
    def __init__(self, KOMPAS_SESSION):
        self.KOMPAS_SESSION = KOMPAS_SESSION

    @asynccontextmanager
    async def __call__(self, state_inc: Optional[str] = Query(None)):
        partner_directory_import = PartnerDirectoryImport(
            state_inc=state_inc,
            session=self.KOMPAS_SESSION
        )
        try:
            yield partner_directory_import
        except asyncio.CancelledError:
            await partner_directory_import.dispose_engine()
            raise Exception("Cancelling request due to disconnect")
        finally:
            await partner_directory_import.dispose_engine()