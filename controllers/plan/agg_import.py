import numpy as np
import pandas as pd
import asyncio

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from datetime import datetime
from sqlalchemy import create_engine, text
from starlette.responses import Response

from utils.utils import get_data


field_names = {
    'partner$inc': 'ID партнера',
    'partner$town$name': 'Город партнера',
    'partner$name': 'Заказчик',
    'pc$name': 'Категория партнера',
    'partner$adate': 'Дата ввода',
    'partner$internet': 'Доступ через Интернет',
    'supervisor$name': 'Куратор',
    'all_pax': 'TOTAL PAX',
    'claim$paidstatus': 'Статус заявки',
    'claim$rdate': 'Дата создания',
    'claim$cdate': 'Дата расчета',
    'claim$cdatetime': 'Дата/Время расчета',
    'claim$datebeg': 'Дата начала',
    'claim$dateend': 'Дата окончания',
    'claim$status': 'Статус 2'
}

convert_timestamp_to_str_list = ['claim$cdatetime', 'claim$datebeg', 'claim$dateend', 'claim$rdate']


class AggImport:
    def __init__(self, year_from: str, state_inc: str):
        self.year_from: int = int(year_from)
        self.state_inc: int = int(state_inc) if state_inc else None
        self.date_period_list = []
        self.__imported_data = pd.DataFrame()
        self.__odbc_driver = "ODBC Driver 17 for SQL Server"
        self.KOMPAS_DB_SERVER = get_data("KOMPAS_DB_SERVER")
        self.KOMPAS_DB_USERNAME = get_data("KOMPAS_DB_USERNAME")
        self.KOMPAS_DB_PASSWORD = get_data("KOMPAS_DB_PASSWORD")
        self.KOMPAS_DB_NAME = get_data("KOMPAS_DB_NAME")
        self.connection_string = f"mssql+aioodbc://{self.KOMPAS_DB_USERNAME}:{self.KOMPAS_DB_PASSWORD}@{self.KOMPAS_DB_SERVER}:1433/{self.KOMPAS_DB_NAME}?driver={self.__odbc_driver}"
        self.engine = None

    def __format_selected_rows(self):
        selected_df = self.__imported_data.loc[:, list(field_names.keys())]
        selected_df = selected_df.where(pd.notnull(selected_df), None)
        selected_df = selected_df.replace(np.nan, None)
        selected_df = selected_df.rename(columns=field_names)
        data = selected_df.to_dict(orient='records')

    async def __fetch_and_append_data(self, queries: list):
        engine = create_async_engine(self.connection_string, echo=False, future=True)
        dataframes = []  # List to hold DataFrames
        try:
            async with engine.connect() as db_conn:
                tasks = [self.__execute_query(db_conn, query) for query in queries]
                results = await asyncio.gather(*tasks)
                dataframes.extend(results)  # Collect all DataFrames
            self.__imported_data = pd.concat(dataframes, ignore_index=True)
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

    def __get_date_periods(self):
        current_year = datetime.now().year
        year_diffence = current_year - self.year_from + 1
        for i in range(0, year_diffence):
            self.date_period_list.append([f'{self.year_from+i}0101', f'{self.year_from+i}1231'])

    async def __fetch_kompas_data(self):
        import_queries = []
        print(self.date_period_list)
        for date_period in self.date_period_list:

            import_query = f"""
                SET NOCOUNT ON;
                EXEC	{get_data("PLAN_PROCEDURE_NAME")}
                @cdate_from = N'{date_period[0]}',
                @cdate_till = N'{date_period[1]}',
                {f'@state_inc = {self.state_inc}' if self.state_inc else ''}
            """
            import_queries.append(import_query)
        await self.__fetch_and_append_data(import_queries)

    async def __process_imported_data(self):
        pivot_imported_data = self.__imported_data.pivot_table(
            index=['partner_inc', 'partner_name', 'partner$town$name', 'partner$adate', 'partner$internet', 'partner$parttype$name', 'pc$name', 'supervisor_name'],  # Columns to group by
            columns='claim_cdate_year',
            values='Pax',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        pivot_imported_data['partner$adate'] = pd.to_datetime(pivot_imported_data['partner$adate'], errors='coerce').dt.date
        return pivot_imported_data.to_dict(orient='records')

    async def dispose_engine(self):
        if self.engine:
            await self.engine.dispose()

    async def run(self):
        self.__get_date_periods()
        await self.__fetch_kompas_data()
        processed_data = await self.__process_imported_data()
        resulted_data = jsonable_encoder(processed_data)
        return Response(
            content=resulted_data,
            status_code=200
        )
