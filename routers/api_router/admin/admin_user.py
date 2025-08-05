from fastapi import APIRouter, Depends

from callers.import_generic import build_body_list_dependency
from controllers.admin.create_admin import CreateAdmin
from database.sessions import WEB_SESSION_FACTORY
from decorators.response import unified_response
from pydantic_models.request_models import CreateUserModel
from utils.utils import get_api_key

router = APIRouter(
    dependencies=[Depends(get_api_key)],
    prefix="/admin"
)


@router.post('/user')
@unified_response
async def create_admin_auth(
    cls_factory: CreateAdmin = Depends(
        build_body_list_dependency(
            body_model=CreateUserModel,
            constructor_cls=CreateAdmin
        )()
    )
):
    async with cls_factory as instance:
        instance.set_session(session_factory=WEB_SESSION_FACTORY)
        await instance.run()
        return "Created"
