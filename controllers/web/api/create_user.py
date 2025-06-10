from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from dao.web_dao import create_user
from models.sqlalchemy_v2.web import WebUser
from pydantic_models.request_models import CreateUserModel
from utils.hashing import Hasher


class CreateUser:
    def __init__(self, user: CreateUserModel):
        self.session_factory: async_sessionmaker = None
        self.user = user

    def set_session(self, session_factory):
        self.session_factory = session_factory

    async def run(self):
        user_model_instance = WebUser()
        user_model_instance.name = self.user.name
        user_model_instance.hashed_password = Hasher().get_password_hash(self.user.password)
        try:
            async with self.session_factory() as session:
                await create_user(session, user_model_instance)
        except IntegrityError as exp:
            raise exp
