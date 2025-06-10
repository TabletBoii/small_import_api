from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from models.models import PlanData, PlanPercentData
from pydantic_models.request_models import PlanPercentModel


class UploadPlanPercentData:
    def __init__(self, plan_percent_data: list[PlanPercentModel]):
        self.session_factory: async_sessionmaker = None
        self.plan_percent_data: PlanPercentModel | list[PlanPercentModel] = plan_percent_data
        self.__odbc_driver = "ODBC Driver 17 for SQL Server"
        self.engine = None

    def set_session(self, session_factory):
        self.session_factory = session_factory

    async def insert_pydantic_model(self):
        instances = [PlanPercentData(**model.dict()) for model in self.plan_percent_data]
        print(instances)
        async with self.session_factory() as session:
            session.add_all(instances)
            await session.commit()

    # Example Usage

    async def run(self):
        async with self.session_factory() as session:
            async with session.begin():
                await session.execute(text("TRUNCATE TABLE plan_percent_values"))

        await self.insert_pydantic_model()


