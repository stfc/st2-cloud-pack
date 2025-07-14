from enum import auto
from meta.enums.auto_name import _AutoName


# pylint: disable=too-few-public-methods
class Protocol(_AutoName):
    TCP = auto()
    UDP = auto()
    ICMP = auto()
    ANY = auto()
