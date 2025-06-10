from fastapi import APIRouter, Depends

from callers.import_generic import build_body_list_dependency
from controllers.web.api.create_user import CreateUser
from database.sessions import WEB_SESSION_FACTORY
from decorators.response import unified_response
from pydantic_models.request_models import CreateUserModel
from utils.utils import get_api_key

router = APIRouter(
    dependencies=[Depends(get_api_key)],
    prefix="/user"
)


@router.post('/')
@unified_response
async def upload_plan_percent_values(
    cls_factory: CreateUser = Depends(
        build_body_list_dependency(
            body_model=CreateUserModel,
            constructor_cls=CreateUser
        )()
    )
):
    async with cls_factory as instance:
        instance.set_session(session_factory=WEB_SESSION_FACTORY)
        await instance.run()
        return "Created"
