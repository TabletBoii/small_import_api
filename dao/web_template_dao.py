from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.sqlalchemy_v2.web import WebTemplate
from pydantic_models.template import TemplateCreate


async def get_template_list(session: AsyncSession, user_id: int, web_resource_inc: int):
    stmt = (select(WebTemplate)
            .where(WebTemplate.user_inc == user_id)
            .where(WebTemplate.web_resource_inc == web_resource_inc)
            )
    result = await session.execute(stmt)
    return result.scalars().all()


# def create_template(session: AsyncSession, user_id: int, template: TemplateCreate):
#     db_tpl = WebTemplate(user_id=user_id, report_key=template.report_key, name=template.name)
#     db.add(db_tpl)
#     db.flush()
#     items = [WebTemplateItem(template_id=db_tpl.id, field_name=f) for f in tpl.fields]
#     db.add_all(items)
#     db.commit()
#     db.refresh(db_tpl)
#     return db_tpl
