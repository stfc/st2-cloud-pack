from enum import Enum, auto


# pylint: disable=too-few-public-methods
class UserDomains(Enum):
    """
    Holds a list of domains where users can be found
    """

    DEFAULT = auto()
    STFC = auto()
    OPENID = auto()  # irisiam - now openid since Stein
    JASMIN = auto()

    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        return UserDomains[val.upper()]
