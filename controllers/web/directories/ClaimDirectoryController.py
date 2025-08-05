import os
import uuid
from pathlib import Path

import aiofiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from controllers.abstract_file_generator_controller import AbstractFileGeneratorController
from dao.samo.claim_procedure import ClaimProcedure
from dao.web.download_list_dao import change_progress_on_done
from database.sessions import WEB_SESSION_FACTORY
from utils.file_export.excel_export import ExportExcel
from utils.file_export.excel_export_streaming import StreamingExcelExporter


class ClaimDirectoryController(AbstractFileGeneratorController):
    def __init__(
        self,
        date_beg_from,
        date_beg_till,
        claim_create_date_from,
        claim_create_date_till,
        confirm_date_from,
        confirm_date_till,
        r_date_from,
        r_date_till,
        field_list,
        file_path,
        download_id
    ):
        self.session_factory: async_sessionmaker = None
        self.date_beg_from = date_beg_from
        self.date_beg_till = date_beg_till
        self.claim_create_date_from = claim_create_date_from
        self.claim_create_date_till = claim_create_date_till
        self.confirm_date_from = confirm_date_from
        self.confirm_date_till = confirm_date_till
        self.r_date_from = r_date_from
        self.r_date_till = r_date_till
        self.field_list = field_list
        self.date_begin_tuple = (self.date_beg_from, self.date_beg_till) if self.date_beg_from != "" else None
        self.claim_create_date_tuple = (self.claim_create_date_from, self.claim_create_date_till) if self.claim_create_date_from != "" else None
        self.confirm_date_tuple = (self.confirm_date_from, self.confirm_date_till) if self.confirm_date_from != "" else None
        self.r_date_tuple = (self.r_date_from, self.r_date_till) if self.r_date_from != "" else None
        self.file_path = file_path
        self.download_id = download_id

    def set_session(self, session_factory):
        self.session_factory = session_factory

    async def generate_excel(
            self,
            data,
            header,
            filepath
    ):
        return ExportExcel().export(
            data=data,
            headers=header,
            sheet_name="Справочник заявок",
            file_path=filepath
        )

    async def claim_procedure_data(self):
        async with self.session_factory() as session:
            inst = ClaimProcedure(
                session=session,
                date_begin_tuple=self.date_begin_tuple,
                claim_create_date_tuple=self.claim_create_date_tuple,
                confirm_date_tuple=self.confirm_date_tuple,
                r_date_tuple=self.r_date_tuple,
                selected_fields_list=self.field_list
            )
            result = await inst.get_claims()
        return result

    async def _row_stream(self):
        async with self.session_factory() as session:
            proc = ClaimProcedure(
                session=session,
                date_begin_tuple=self.date_begin_tuple,
                claim_create_date_tuple=self.claim_create_date_tuple,
                confirm_date_tuple=self.confirm_date_tuple,
                r_date_tuple=self.r_date_tuple,
                selected_fields_list=self.field_list
            )
            result = proc.stream_claims_by_batches()
            async for row in result:
                yield row

    async def _run(self):
        claim_result = await self.claim_procedure_data()

        await self.generate_excel(
            claim_result,
            self.field_list,
            self.file_path
        )

    async def _streaming_run(self):

        exporter = StreamingExcelExporter()
        await exporter.export(
            data=self._row_stream(),
            headers=self.field_list,
            sheet_name="Справочник заявок",
            file_path=self.file_path
        )
