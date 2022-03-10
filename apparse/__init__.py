from ._version import (
    __author__,
    __author_email__,
    __license__,
    __title__,
    __url__,
    __version__
)

from .iw_device_parser import IwDeviceParser
from .iw_station_parser import IwStationParser
from .iwinfo_device_parser import IwinfoDeviceParser
from .iwinfo_station_parser import IwinfoStationParser


def parse_iw_device(data):
    return IwDeviceParser().parse(data)


def parse_iw_station(data):
    return IwStationParser().parse(data)


def parse_iwinfo_device(data):
    return IwinfoDeviceParser().parse(data)


def parse_iwinfo_station(data):
    return IwinfoStationParser().parse(data)
