from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from dao.web.admin_user_dao import create_admin_user
from models.web.admin_user_model import AdminAuth
from pydantic_models.request_models import CreateUserModel
from utils.hashing import Hasher


class CreateAdmin:
    def __init__(self, user: CreateUserModel):
        self.session_factory: async_sessionmaker = None
        self.user = user

    def set_session(self, session_factory):
        self.session_factory = session_factory

    async def run(self):
        admin_model_instance = AdminAuth()
        admin_model_instance.username = self.user.name
        admin_model_instance.password_hashed = Hasher().get_password_hash(self.user.password)
        admin_model_instance.description = self.user.description
        try:
            async with self.session_factory() as session:
                await create_admin_user(session, admin_model_instance)
        except IntegrityError as exp:
            raise exp
