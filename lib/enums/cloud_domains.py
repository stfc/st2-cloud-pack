from enum import auto

from enums.auto_name import _AutoName


# pylint: disable=too-few-public-methods
class CloudDomains(_AutoName):
    """
    Holds a list of domains where users can be found
    """

    PROD = auto()
    DEV = auto()

    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        return CloudDomains[val.upper()]
