from enum import Enum

from routers.web_router.navigator.abstract import NavBase


class PowerBiBaseTemplateNavigator(NavBase):
    def __init__(self):
        super().__init__("/{route_param}", None, "power_bi_base")


class PowerBiEmbedParamsNavigator(NavBase):
    def __init__(self):
        super().__init__("/embed-params/{route_param}", None, "embed_params")


class PowerBiTelemetryNavigator(NavBase):
    def __init__(self):
        super().__init__("/telemetry/{route_param}", None, "power_bi_telemetry")


class PowerBiBaseActionsNavigator(NavBase):
    def __init__(self):
        super().__init__("/power_bi_base", None, None)
        self._embed_params = PowerBiEmbedParamsNavigator()
        self._power_bi_base_template = PowerBiBaseTemplateNavigator()
        self._power_bi_telemetry = PowerBiTelemetryNavigator()

    @property
    def embed_params(self):
        return self._embed_params

    @property
    def power_bi_base_template(self) -> PowerBiBaseTemplateNavigator:
        return self._power_bi_base_template

    @property
    def power_bi_telemetry(self):
        return self._power_bi_telemetry


class PowerBiTemplateNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "power_bi")


class PowerBiNavigator(NavBase):
    def __init__(self):
        super().__init__("/power_bi", None, None)
        self._power_bi = PowerBiTemplateNavigator()
        self._power_bi_base_actions = PowerBiBaseActionsNavigator()

    @property
    def power_bi(self) -> PowerBiTemplateNavigator:
        return self._power_bi

    @property
    def power_bi_base_actions(self) -> PowerBiBaseActionsNavigator:
        return self._power_bi_base_actions
