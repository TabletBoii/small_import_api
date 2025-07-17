from typing import List

from sqlalchemy import text, delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from models.ext_db.plan_model import PlanModel
from models.ext_db.budget_plan_model import BudgetPlanModel
from models.ext_db.budget_model import BudgetModel
from pydantic_models.request_models import BudgetValuesModel, BudgetPlanModel


class UploadBudgetPlanData:
    def __init__(self, plan_data: List[BudgetPlanModel]):
        self.session_factory: async_sessionmaker = None
        self.plan_data: List[BudgetPlanModel] = plan_data
        self.__odbc_driver = "ODBC Driver 17 for SQL Server"
        self.engine = None

    def set_session(self, session_factory):
        self.session_factory = session_factory

    async def delete_old_data(self, manager):
        async with self.session_factory() as session:
            async with session.begin():
                stmt = delete(BudgetPlanModel).where(BudgetPlanModel.manager == manager)
                await session.execute(stmt)
                await session.commit()

    async def insert_pydantic_model(self):
        instances = [BudgetModel(**model.dict()) for model in self.plan_data]
        async with self.session_factory() as session:
            for instance in instances:
                await self.delete_old_data(instance.manager)
                session.add(instance)
            await session.commit()

    async def run(self):
        await self.insert_pydantic_model()
