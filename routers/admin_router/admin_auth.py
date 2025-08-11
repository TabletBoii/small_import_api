from fastapi import Request, Form
from fastapi.responses import RedirectResponse

from dao.web.admin_user_dao import get_admin_by_username
from database.sessions import WEB_SESSION_FACTORY
from routers.admin_router.admin import admin_jinja_router
from routers.templates import admin_templates
from utils.hashing import Hasher


async def validate_input(username: str, password: str) -> [bool, str | None]:
    if len(username) == 0:
        return False, "Username is required"

    elif len(password) == 0:
        return False, "Password is required"

    else:
        ...
    async with WEB_SESSION_FACTORY() as session:
        user = await get_admin_by_username(session, username)
        if user is None:
            return False, "Invalid credentials"
        elif not Hasher.verify_password(password, user.password_hashed):
            return False, "Invalid credentials"
        else:
            return True, None


@admin_jinja_router.get("/login")
async def login_get(request: Request):
    return admin_templates.TemplateResponse("admin_login.html", {"request": request})


@admin_jinja_router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    validation_result = await validate_input(username, password)
    if not validation_result[0]:
        return admin_templates.TemplateResponse(
            "admin_login.html",
            {"request": request, "error": f"{validation_result[1]}"},
            status_code=401
        )

    request.session["admin"] = username
    return RedirectResponse(url="/admin/", status_code=302)


@admin_jinja_router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=302)
