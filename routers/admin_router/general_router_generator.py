from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy import TextClause
from starlette.responses import RedirectResponse
from typing import Type, Callable, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from dao.general.admin_dao import get_all, update_by_id, delete_by_id, create
from database.sessions import WEB_SESSION_FACTORY
from routers.templates import admin_templates
from utils.utils import row_to_dict


def generate_crud_router(
    model: Type,
    url_prefix: str,
    table_headers: list[str],
    model_name: str,
    model_header_names: List[str],
    dropdown_field_dict: Dict = None,
    get_custom_query=None
) -> APIRouter:
    router = APIRouter(prefix=url_prefix, tags=[model_name])

    async def get_form_context():
        async with WEB_SESSION_FACTORY() as session:
            if get_custom_query is not None:
                records = await get_all(session, model, get_custom_query)
            else:
                records = await get_all(session, model)
            result_list = []
            for data in records:
                data_dict = {}
                for i in range(len(model_header_names)):
                    data_dict[model_header_names[i]] = data[i]
                result_list.append(data_dict)
            if dropdown_field_dict is not None:
                resulted_dropdown_field_dict = {
                    key: {
                        f"{d.inc}": d.name
                        for d in
                        await get_all(session, value[0], value[1])
                    } for (key, value) in dropdown_field_dict.items()
                }
                return {
                    f"{model_name}_list": result_list,
                    "dropdown_field_dict": resulted_dropdown_field_dict,
                    "headers": table_headers
                }
        return {
            f"{model_name}_list": result_list,
            "entity_fields": model.__field_aliases__,
            "headers": table_headers
        }

    @router.get("")
    async def get_table(request: Request, table_ctx=Depends(get_form_context)):
        return admin_templates.TemplateResponse(
            f"{model_name}.html",
            {"request": request, **table_ctx}
        )

    @router.post("/edit/{item_id}")
    async def edit_item(
            request: Request,
            item_id: int
    ):
        form = await request.form()
        data_to_update = dict(form)
        for key, value in data_to_update.items():
            if "is" in key or "has" in key:
                data_to_update[key] = bool(int(value))
        async with WEB_SESSION_FACTORY() as session:
            await update_by_id(session, model, item_id, data_to_update)
        return RedirectResponse(url=f"/admin{url_prefix}", status_code=302)

    @router.get("/delete/{item_id}")
    async def delete_item(
            request: Request,
            item_id: int
    ):
        async with WEB_SESSION_FACTORY() as session:
            await delete_by_id(session, model, item_id)
        return RedirectResponse(url=f"/admin{url_prefix}", status_code=302)

    @router.post("/create")
    async def create_item(
            request: Request
    ):
        form = dict(await request.form())
        for key, value in form.items():
            if "is" in key or "has" in key:
                form[key] = bool(value)
        data_to_create = model(**form)
        async with WEB_SESSION_FACTORY() as session:
            await create(session, data_to_create)
        return RedirectResponse(url=f"/admin{url_prefix}", status_code=302)

    return router


