from enum import Enum
from typing import Self

from routers.web_router.navigator.abstract import NavBase
from routers.web_router.navigator.access_request_navigator import AccessRequestNavigator
from routers.web_router.navigator.auth_navigator import AuthNavigator
from routers.web_router.navigator.directory_navigator import DirectoriesNavigator
from routers.web_router.navigator.download_navigator import DownloadNavigator
from routers.web_router.navigator.home_navigator import HomeNavigator
from routers.web_router.navigator.power_bi_navigator import PowerBiNavigator
from routers.web_router.navigator.report_navigator import ReportNavigator


class Navigator(NavBase):
    def __init__(self):
        super().__init__("/", None, "")
        self._home = HomeNavigator()
        self._reports = ReportNavigator()
        self._directories = DirectoriesNavigator()
        self._powerbi_base = PowerBiNavigator()
        self._download = DownloadNavigator()
        self._auth = AuthNavigator()
        self._access_request = AccessRequestNavigator()

    @property
    def home(self) -> HomeNavigator:
        return self._home

    @property
    def reports(self) -> ReportNavigator:
        return self._reports

    @property
    def directories(self) -> DirectoriesNavigator:
        return self._directories

    @property
    def powerbi_base(self) -> PowerBiNavigator:
        return self._powerbi_base

    @property
    def download(self) -> DownloadNavigator:
        return self._download

    @property
    def auth(self) -> AuthNavigator:
        return self._auth

    @property
    def access_request(self) -> AccessRequestNavigator:
        return self._access_request

    @property
    def navigator(self) -> Self:
        return self
