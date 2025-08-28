from enum import Enum

from routers.web_router.navigator.abstract import NavBase


class DownloadTemplateNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "download")


class DownloadGetDownloadNavigator(NavBase):
    def __init__(self):
        super().__init__("/get_downloads", None, "get_downloads")


class DownloadReportNavigator(NavBase):
    def __init__(self):
        super().__init__("/{download_id}", None, "download_report")


class DownloadNavigator(NavBase):
    def __init__(self):
        super().__init__("/download", None, None)
        self._download_template = DownloadTemplateNavigator()
        self._get_downloads = DownloadGetDownloadNavigator()
        self._download_report = DownloadReportNavigator()

    @property
    def download_template(self) -> DownloadTemplateNavigator:
        return self._download_template

    @property
    def get_downloads(self) -> DownloadGetDownloadNavigator:
        return self._get_downloads

    @property
    def download_report(self) -> DownloadReportNavigator:
        return self._download_report
