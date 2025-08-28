from enum import Enum

from routers.web_router.navigator.abstract import NavBase


class AccessRequestTemplateNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "access_request")


class AccessRequestFormNavigator(NavBase):
    def __init__(self):
        super().__init__("/{resource_id}", None, "make_request")


class AccessRequestNavigator(NavBase):
    def __init__(self):
        super().__init__("/access_request", None, None)
        self._template = AccessRequestTemplateNavigator()
        self._form = AccessRequestFormNavigator()

    @property
    def template(self) -> AccessRequestTemplateNavigator:
        return self._template

    @property
    def form(self) -> AccessRequestFormNavigator:
        return self._form
