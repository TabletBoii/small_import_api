from typing import List

from fastapi import APIRouter, Depends

from dao.web.web_user_dao import get_user_by_username
from dao.web.resource_dao import get_web_resource_by_name
from dao.web.template_dao import get_template_list
from database.sessions import WEB_SESSION_FACTORY
from pydantic_models.template import TemplateResponse
from utils.utils import require_user

router = APIRouter(
    # dependencies=[Depends(get_api_key)],get_api_key
    prefix="/template"
)


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(page_name: str, user: str = Depends(require_user)):
    async with WEB_SESSION_FACTORY() as session:
        user_instance = await get_user_by_username(session=session, username=user)
        page_instance = await get_web_resource_by_name(session=session, web_resource_name=page_name)
        resulted_template_list = await get_template_list(
            session,
            user_id=user_instance.inc,
            web_resource_inc=page_instance.inc
        )

    return resulted_template_list


# @router.post('/', response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
# def create_new_template(template: TemplateCreate, user: str = Depends(require_user)):
#     return create_template(db, current_user.id, template)
#
# @router.get('/{template_id}/items', response_model=List[str])
# def read_template_items(template_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     return get_template_items(db, current_user.id, template_id)
#
# @router.delete('/{template_id}', status_code=status.HTTP_204_NO_CONTENT)
# def remove_template(template_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     delete_template(db, current_user.id, template_id)
#
