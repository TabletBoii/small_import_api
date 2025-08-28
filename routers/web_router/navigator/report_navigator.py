from routers.web_router.navigator.abstract import NavBase


class ReportDmcTemplateNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, 'report_dmc')


class ReportDmcFormNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, 'report_dmc_form')


class ReportDmcPartnerNavigator(NavBase):
    def __init__(self):
        super().__init__("/partner/items", None, 'report_dmc_partner_filter')


class ReportDmcCountryNavigator(NavBase):
    def __init__(self):
        super().__init__("/country/items", None, 'report_dmc_country_filter')


class ReportDmcNavigator(NavBase):
    def __init__(self):
        super().__init__("/report_dmc", None, None)

        self._template = ReportDmcTemplateNavigator()
        self._form = ReportDmcFormNavigator()
        self._partner_filter = ReportDmcPartnerNavigator()
        self._country_filter = ReportDmcCountryNavigator()

    @property
    def template(self) -> ReportDmcTemplateNavigator:
        return self._template

    @property
    def form(self) -> ReportDmcFormNavigator:
        return self._form

    @property
    def partner_filter(self) -> ReportDmcPartnerNavigator:
        return self._partner_filter

    @property
    def country_filter(self) -> ReportDmcCountryNavigator:
        return self._country_filter


class AvgTimeReportTemplateNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "report_avg")


class AvgTimeReportFormNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "report_avg_form")


class AvgTimeReportNavigator(NavBase):
    def __init__(self):
        super().__init__("/report_avg", None, None)

        self._template = AvgTimeReportTemplateNavigator()

        self._form = AvgTimeReportFormNavigator()

    @property
    def template(self) -> AvgTimeReportTemplateNavigator:
        return self._template

    @property
    def form(self) -> AvgTimeReportFormNavigator:
        return self._form


class ReportIndexNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "reports")


class ReportNavigator(NavBase):

    def __init__(self):
        super().__init__("/report", None, "reports")
        self._index = ReportIndexNavigator()
        self._report_dmc = ReportDmcNavigator()
        self._avg_time_report = AvgTimeReportNavigator()

    @property
    def index(self) -> ReportIndexNavigator:
        return self._index

    @property
    def report_dmc(self) -> ReportDmcNavigator:
        return self._report_dmc

    @property
    def avg_time_report(self) -> AvgTimeReportNavigator:
        return self._avg_time_report
