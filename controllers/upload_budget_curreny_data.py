from typing import List

from sqlalchemy import text, delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from models.models import PlanData, BudgetData, BudgetCurrencyData
from pydantic_models.request_models import BudgetCurrencyModel


class UploadBudgetCurrencyData:
    def __init__(self, currency_data: List[BudgetCurrencyModel]):
        self.session_factory: async_sessionmaker = None
        self.currency_data: List[BudgetCurrencyModel] = currency_data
        self.__odbc_driver = "ODBC Driver 17 for SQL Server"
        self.engine = None

    def set_session(self, session_factory):
        self.session_factory = session_factory

    async def truncate_data(self):
        async with self.session_factory() as session:
            async with session.begin():
                stmt = delete(BudgetCurrencyData)
                await session.execute(stmt)
                await session.commit()

    async def insert_pydantic_model(self):
        instances = [BudgetCurrencyData(**model.dict()) for model in self.currency_data]
        async with self.session_factory() as session:
            await self.truncate_data()
            session.add_all(instances)
            await session.commit()

    async def run(self):
        # async with self.session_factory() as session:
        #     async with session.begin():
        #         await session.execute(text("TRUNCATE TABLE plan_data"))
        #
        await self.insert_pydantic_model()
