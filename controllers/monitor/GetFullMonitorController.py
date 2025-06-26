import asyncio
import logging
import time
from typing import Tuple

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from pydantic_models.request_models import GetFullMonitorParams
from utils.date_period_batch import get_date_batches


class GetFullMonitor:
    def __init__(self, model: GetFullMonitorParams):
        self.model_instance = model
        self.session_factory: async_sessionmaker = None

    def set_session(self, session_factory):
        self.session_factory = session_factory

    async def __execute_query(self, query: str):
        try:
            async with self.session_factory() as session:
                logging.info(f"Начат запрос: {query}")
                result = await session.execute(text(query))

                mappings = result.mappings().all()
                logging.info(f"Запрос {query} завершен")
                return [dict(row) for row in mappings]
        except Exception as e:
            raise e

    async def __fetch_and_append_data(self, query_list: list[str]):
        start_time = time.time()

        semaphore = asyncio.Semaphore(10)

        async def sem_execute_query(query):
            async with semaphore:
                return await self.__execute_query(query)

        tasks = [asyncio.create_task(sem_execute_query(query)) for query in query_list]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_time = time.time() - start_time
        print(f"Total query execution and data processing time: {total_time:.2f} seconds")
        return results

    async def generate_monitor_query(self, date_period: Tuple[str, str]):
        state_inc_str = ","
        state_inc_str = state_inc_str.join(map(str, self.model_instance.state_list))
        match self.model_instance.monitor_type:
            case "full":
                stored_procedure_name = "up_flight_monitor_vertical"
            case "direct":
                stored_procedure_name = "up_flight_monitor_vertical_powerbi"
            case _:
                raise "??????"

        raw_query = f"""
            SET NOCOUNT ON;
            DECLARE @p_townfrom IncList;
            INSERT INTO @p_townfrom (inc)
            SELECT t.inc
              FROM town AS t
             WHERE t.state IN ({state_inc_str});
            
            DECLARE @p_townto IncList;
            INSERT INTO @p_townto (inc)
            SELECT inc
              FROM town;            
            
            EXEC {stored_procedure_name}
                 @p_datebeg   = '{date_period[0]}'
               , @p_dateend   = '{date_period[1]}'
               , @p_townfrom  = @p_townfrom
               , @p_townto    = @p_townto;
        """
        return raw_query

    async def __test_execute_query(self, query):
        async with self.session_factory() as session:
            result = await session.execute(text(query))
            return result.all()

    async def run(self):
        batch_month = 2
        date_batch_list = get_date_batches(
            self.model_instance.date_beg_from,
            self.model_instance.date_beg_till,
            batch_months=batch_month
        )
        logging.info("Получены date batches")
        query_list = [await self.generate_monitor_query(date_batch) for date_batch in date_batch_list]
        logging.info("Сформированы запросы")
        result = await self.__fetch_and_append_data(query_list)
        return result
