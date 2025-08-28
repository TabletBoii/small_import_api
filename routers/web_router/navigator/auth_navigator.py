from enum import Enum

from routers.web_router.navigator.abstract import NavBase


class AuthTemplateNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "login_get")


class AuthFormNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "login_post")


class AuthMicrosoftLoginNavigator(NavBase):
    def __init__(self):
        super().__init__("/microsoft", None, "login_via_microsoft")


class AuthCallbackNavigator(NavBase):
    def __init__(self):
        super().__init__("/aad/callback", None, "auth_callback")


class AuthNavigator(NavBase):
    def __init__(self):
        super().__init__("/login", None, None)
        self._template = AuthTemplateNavigator()
        self._form = AuthFormNavigator()
        self._microsoft_login = AuthMicrosoftLoginNavigator()
        self._auth_callback = AuthCallbackNavigator()

    @property
    def template(self) -> AuthTemplateNavigator:
        return self._template

    @property
    def form(self) -> AuthFormNavigator:
        return self._form

    @property
    def microsoft_login(self) -> AuthMicrosoftLoginNavigator:
        return self._microsoft_login

    @property
    def auth_callback(self) -> AuthCallbackNavigator:
        return self._auth_callback
