import numpy as np
import pandas as pd
import asyncio

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection, async_sessionmaker, AsyncSession
from sqlalchemy import text
from utils.utils import get_data


convert_timestamp_to_str_list = ['partner_adate', 'partner_edate', 'partner_stopdate']


class PartnerDirectoryImport:
    def __init__(self, state_inc: str):
        self.session_factory = None
        self.state_inc: int = int(state_inc) if state_inc else None
        self.__imported_data = pd.DataFrame()
        self.engine = None

    async def __fetch_and_append_data(self, query: str):
        async with self.session_factory() as session:
            try:
                result = await self.__execute_query(session, query)
                self.__imported_data = result
            except Exception as e:
                raise e

    async def __execute_query(self, session: AsyncSession, query: str):
        try:
            result = await session.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            df = pd.DataFrame(rows, columns=columns)
            return df
        except Exception as e:
            raise e

    async def __fetch_kompas_data(self):
        import_query = f"""
            SET NOCOUNT ON;
            EXEC {get_data("PARTNER_DIRECTORY_PROCEDURE_NAME")}
            {f'@state_inc = {self.state_inc}' if self.state_inc else ''}
        """
        await self.__fetch_and_append_data(import_query)

    def set_session(self, session_factory):
        self.session_factory = session_factory

    async def run(self):
        await self.__fetch_kompas_data()
        # processed_data = await self.__process_imported_data()
        self.__imported_data = self.__imported_data.where(pd.notnull(self.__imported_data), None)
        self.__imported_data = self.__imported_data.replace(np.nan, None)
        self.__imported_data[convert_timestamp_to_str_list] = self.__imported_data[
            convert_timestamp_to_str_list].astype(str)
        self.__imported_data[convert_timestamp_to_str_list] = self.__imported_data[convert_timestamp_to_str_list].apply(lambda x: x.str.replace('T', ' '))
        for col in convert_timestamp_to_str_list:
            self.__imported_data[col] = pd.to_datetime(self.__imported_data[col], errors='coerce').dt.date
        self.__imported_data = self.__imported_data.to_dict(orient='records')
        resulted_data = jsonable_encoder(self.__imported_data)
        return resulted_data
