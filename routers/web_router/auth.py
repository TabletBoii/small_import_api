from fastapi import Request, Form
from fastapi.responses import RedirectResponse

from dao.web.web_dao import get_user_by_username
from database.sessions import WEB_SESSION_FACTORY
from routers.web_router.web import web_jinja_router, templates
from utils.hashing import Hasher


async def validate_input(username: str, password: str) -> [bool, str | None]:
    if len(username) == 0:
        return False, "Username is required"

    elif len(password) == 0:
        return False, "Password is required"

    else:
        ...
    async with WEB_SESSION_FACTORY() as session:
        user = await get_user_by_username(session, username)
        if user is None:
            return False, "Invalid credentials"
        elif not Hasher.verify_password(password, user.hashed_password):
            return False, "Invalid credentials"
        else:
            return True, None


@web_jinja_router.get("/login")
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@web_jinja_router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    validation_result = await validate_input(username, password)
    if not validation_result[0]:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": f"{validation_result[1]}"},
            status_code=401
        )

    request.session["user"] = username
    return RedirectResponse(url="/web/home", status_code=302)


# @web_jinja_router.get("/logout")
# async def logout(request: Request):
#     request.session.clear()
#     return RedirectResponse(url="/login", status_code=302)
