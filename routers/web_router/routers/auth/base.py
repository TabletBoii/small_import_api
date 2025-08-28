import time
from datetime import datetime, timedelta

from fastapi import Request, Form, APIRouter
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException

from dao.web.web_user_dao import create_user, get_user_by_username, is_user_exists_by_microsoft_oid
from database.sessions import WEB_SESSION_FACTORY
from models.web.web_user_model import WebUserModel
from routers.web_router.navigator.navigator_base import Navigator
from routers.web_router.web_base import templates, navigation
from sub_app.msal_app import msal_app
from utils.hashing import Hasher
from utils.msal_scopes import AUTH_SCOPE

auth_router = APIRouter(
    prefix=navigation.auth.path,
    tags=["Авторизация"],
)


async def validate_input(username: str, password: str) -> [bool, str | None]:
    if len(username) == 0:
        return False, "Username is required"

    elif len(password) == 0:
        return False, "Password is required"

    else:
        ...
    async with WEB_SESSION_FACTORY() as session:
        # TODO: проверить вход с пустым полем password пользователей, вошедших через microsoft
        user = await get_user_by_username(session, username)
        if user.hashed_password == "":
            return False, "Invalid credentials"
        if user is None:
            return False, "Invalid credentials"
        elif not Hasher.verify_password(password, user.hashed_password):
            return False, "Invalid credentials"
        elif not user.is_activated:
            return False, "Account has been deactivated"
        else:
            return True, None


def build_auth_url(request: Request) -> str:
    return msal_app.get_authorization_request_url(
        scopes=AUTH_SCOPE,
        redirect_uri=str(request.url_for("auth_callback"))
    )


def exchange_code_for_token(request: Request) -> dict:
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(400, "Code not found in callback")
    result = msal_app.acquire_token_by_authorization_code(
        code=code,
        scopes=AUTH_SCOPE,
        redirect_uri=str(request.url_for("auth_callback"))
    )
    if "access_token" not in result:
        raise HTTPException(500, f"Token acquisition failed: {result.get('error_description')}")
    return result


async def create_user_if_not_exists(microsoft_oid: str, username: str):
    async with WEB_SESSION_FACTORY() as session:
        if await is_user_exists_by_microsoft_oid(session, microsoft_oid):
            return
        await create_user(
            session,
            WebUserModel(
                name=username,
                hashed_password='',
                description='',
                microsoft_email=username,
                microsoft_oid=microsoft_oid,
            )
        )
        await session.commit()


@auth_router.get(navigation.auth.template.path)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@auth_router.post(navigation.auth.form.path)
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


@auth_router.get(navigation.auth.microsoft_login.path)
async def login_via_microsoft(
        request: Request
):
    auth_url = build_auth_url(request)
    return RedirectResponse(auth_url)


@auth_router.get(navigation.auth.auth_callback.path, name="auth_callback")
async def auth_callback(request: Request):
    token_result = exchange_code_for_token(request)

    id_token = token_result.get("id_token")
    access_token = token_result["access_token"]
    refresh_token = token_result["refresh_token"]
    expires_in = token_result.get("expires_in")

    expires_at = time.time() + int(expires_in)
    session_store = request.app.state.session_store
    claims = token_result.get("id_token_claims", {})
    microsoft_oid = claims.get("oid")
    email = claims.get("preferred_username") or claims.get("email")

    await create_user_if_not_exists(microsoft_oid, email)

    session_id = session_store.create(
        email=email,
        id_token=id_token,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at
    )
    response = RedirectResponse(url="/web/home", status_code=302)
    expires = (datetime.now() + timedelta(days=7))
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        path="/"
    )
    request.session["user"] = email
    return response
