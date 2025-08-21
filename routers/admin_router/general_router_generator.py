from urllib.parse import urlencode

from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy import TextClause
from starlette.responses import RedirectResponse
from typing import Type, Callable, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from dao.general.admin_dao import get_all, update_by_id, delete_by_id, create
from database.dependencies import get_web_session, get_kompas_session
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

    async def get_form_context(
            web_sess: AsyncSession = Depends(get_web_session),
            ddl_sess: AsyncSession = Depends(get_kompas_session),
    ) -> Dict[str, Any]:
        if get_custom_query is not None:
            records = await get_all(web_sess, model, get_custom_query)
        else:
            records = await get_all(web_sess, model)

        result_list: List[Dict[str, Any]] = []
        for row in records:
            d: Dict[str, Any] = {}
            for i, col in enumerate(model_header_names):
                d[col] = row[i]
            result_list.append(d)

        if dropdown_field_dict:
            resulted_dropdown_field_dict = {
                key: {
                    f"{d.inc}": d.name
                    for d in
                    await get_all(ddl_sess if db_name == 'KOMPAS' else web_sess, dropdown_model, query)
                } for key, (dropdown_model, query, db_name) in dropdown_field_dict.items()
            }

            return {
                f"{model_name}_list": result_list,
                "dropdown_field_dict": resulted_dropdown_field_dict,
                "headers": table_headers,
            }

        return {
            f"{model_name}_list": result_list,
            "headers": table_headers,
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
        try:
            form = await request.form()
            data_to_update = dict(form)
            print(data_to_update)
            for key, value in data_to_update.items():
                if "is" in key or "has" in key:
                    if value.lower() in ["true", "да", "истина"]:
                        data_to_update[key] = True
                    elif value.lower() in ["false", "нет", "ложь"]:
                        data_to_update[key] = False
                    else:
                        data_to_update[key] = bool(int(value))
            async with WEB_SESSION_FACTORY() as session:
                await update_by_id(session, model, item_id, data_to_update)
            ok = urlencode({"ok": "Изменено"})
            return RedirectResponse(url=f"/admin{url_prefix}?{ok}", status_code=302)
        except Exception as e:
            print(e)
            err = urlencode({"err": "Не удалось сохранить изменения."})
            return RedirectResponse(url=f"/admin{url_prefix}?{err}", status_code=303)

    @router.get("/delete/{item_id}")
    async def delete_item(
            request: Request,
            item_id: int
    ):
        try:
            async with WEB_SESSION_FACTORY() as session:
                await delete_by_id(session, model, item_id)
            return RedirectResponse(url=f"/admin{url_prefix}", status_code=302)
        except Exception as e:
            print(e)
            err = urlencode({"err": "Неизвестная ошибка"})
            return RedirectResponse(url=f"/admin{url_prefix}?{err}", status_code=303)

    @router.post("/create")
    async def create_item(
            request: Request
    ):
        try:
            form = dict(await request.form())
            for key, value in form.items():
                if "is" in key or "has" in key:
                    if value.lower() in ["true", "да", "истина"]:
                        form[key] = True
                    elif value.lower() in ["false", "нет", "ложь"]:
                        form[key] = False
                    else:
                        form[key] = bool(int(value))
            data_to_create = model(**form)
            async with WEB_SESSION_FACTORY() as session:
                await create(session, data_to_create)
            return RedirectResponse(url=f"/admin{url_prefix}", status_code=302)
        except Exception as e:
            print(e)
            err = urlencode({"err": "Неизвестная ошибка"})
            return RedirectResponse(url=f"/admin{url_prefix}?{err}", status_code=303)

    return router


