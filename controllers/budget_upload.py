from typing import List

from sqlalchemy import text, delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from models.models import PlanData, BudgetData
from pydantic_models.request_models import BudgetValuesModel


class UploadBudgetData:
    def __init__(self, budget_data: List[BudgetValuesModel]):
        self.session_factory: async_sessionmaker = None
        self.budget_data: List[BudgetValuesModel] = budget_data
        self.__odbc_driver = "ODBC Driver 17 for SQL Server"
        self.engine = None

    def set_session(self, session_factory):
        self.session_factory = session_factory

    async def delete_old_data(self):
        async with self.session_factory() as session:
            async with session.begin():
                stmt = delete(BudgetData).where(BudgetData.department == self.budget_data[0].department)
                await session.execute(stmt)
                await session.commit()

    async def insert_pydantic_model(self):
        if isinstance(self.budget_data, list):
            user_instances = [BudgetData(**model.dict()) for model in self.budget_data]
            async with self.session_factory() as session:
                await self.delete_old_data()
                session.add_all(user_instances)
                await session.commit()
        else:
            user_instance = BudgetData(**self.budget_data.dict())
            async with self.session_factory() as session:
                session.add(user_instance)
                await session.commit()

    async def run(self):
        # async with self.session_factory() as session:
        #     async with session.begin():
        #         await session.execute(text("TRUNCATE TABLE plan_data"))
        #
        await self.insert_pydantic_model()
