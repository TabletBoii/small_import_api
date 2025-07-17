from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from models.ext_db.plan_model import PlanModel
from pydantic_models.request_models import PlanValuesModel


class UploadPlanData:
    def __init__(self, plan_data: list[PlanValuesModel]):
        self.session_factory: async_sessionmaker = None
        self.plan_data: PlanValuesModel | list[PlanValuesModel] = plan_data
        self.__odbc_driver = "ODBC Driver 17 for SQL Server"
        self.engine = None

    def set_session(self, session_factory):
        self.session_factory = session_factory

    async def insert_pydantic_model(self):
        if isinstance(self.plan_data, list):
            user_instances = [PlanModel(**model.dict()) for model in self.plan_data]
            print(user_instances)
            async with self.session_factory() as session:
                session.add_all(user_instances)
                await session.commit()
        else:
            user_instance = PlanModel(**self.plan_data.dict())
            async with self.session_factory() as session:
                session.add(user_instance)
                await session.commit()

    # Example Usage

    async def run(self):
        async with self.session_factory() as session:
            async with session.begin():
                await session.execute(text("TRUNCATE TABLE plan_data"))

        await self.insert_pydantic_model()


