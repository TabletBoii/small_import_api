from enum import Enum


class MonitorTypeEnum(str, Enum):
    full_monitor = "full"
    direct_flights_monitor_only = "direct"
