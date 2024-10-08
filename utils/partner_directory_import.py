import numpy as np
import pandas as pd
import asyncio

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from sqlalchemy import text
from utils.utils import get_data


convert_timestamp_to_str_list = ['partner_adate', 'partner_edate', 'partner_stopdate']


class PartnerDirectoryImport:
    def __init__(self, state_inc: str):
        self.state_inc: int = int(state_inc) if state_inc else None
        self.__imported_data = pd.DataFrame()
        self.__odbc_driver = "ODBC Driver 17 for SQL Server"
        self.KOMPAS_DB_SERVER = get_data("KOMPAS_DB_SERVER")
        self.KOMPAS_DB_USERNAME = get_data("KOMPAS_DB_USERNAME")
        self.KOMPAS_DB_PASSWORD = get_data("KOMPAS_DB_PASSWORD")
        self.KOMPAS_DB_NAME = get_data("KOMPAS_DB_NAME")
        self.connection_string = f"mssql+aioodbc://{self.KOMPAS_DB_USERNAME}:{self.KOMPAS_DB_PASSWORD}@{self.KOMPAS_DB_SERVER}:1433/{self.KOMPAS_DB_NAME}?driver={self.__odbc_driver}"
        self.engine = None

    async def __fetch_and_append_data(self, query: str):
        engine = create_async_engine(self.connection_string, echo=False, future=True)
        try:
            async with engine.connect() as db_conn:
                task = self.__execute_query(db_conn, query)
                result = await asyncio.gather(task)
            self.__imported_data = result[0]
        except Exception as e:
            raise e
        finally:
            await engine.dispose()

    async def __execute_query(self, db_conn: AsyncConnection, query: str):
        try:
            result = await db_conn.execute(text(query))
        except Exception as e:
            # print(e)
            raise e
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
        return df

    async def __fetch_kompas_data(self):

        import_query = f"""
            SET NOCOUNT ON;
            EXEC	{get_data("PARTNER_DIRECTORY_PROCEDURE_NAME")}
            {f'@state_inc = {self.state_inc}' if self.state_inc else ''}
        """
        await self.__fetch_and_append_data(import_query)

    async def dispose_engine(self):
        if self.engine:
            await self.engine.dispose()

    async def run(self):
        await self.__fetch_kompas_data()
        # processed_data = await self.__process_imported_data()
        self.__imported_data = self.__imported_data.where(pd.notnull(self.__imported_data), None)
        self.__imported_data = self.__imported_data.replace(np.nan, None)
        self.__imported_data[convert_timestamp_to_str_list] = self.__imported_data[convert_timestamp_to_str_list].apply(
            lambda x: x.str.replace('T', ' '))
        self.__imported_data = self.__imported_data.to_dict(orient='records')
        resulted_data = jsonable_encoder(self.__imported_data)
        return resulted_data
