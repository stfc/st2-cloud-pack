from enum import Enum
from typing import Optional


class ServerStatus(Enum):
    """
    Server states we currently use in our code, this can be extended to include other states in the future.
    """

    ACTIVE = "ACTIVE"
    ERROR = "ERROR"
    SHELVED = "SHELVED"
    SHELVED_OFFLOADED = "SHELVED_OFFLOADED"
    SHUTOFF = "SHUTOFF"
    NONE = None

    @classmethod
    def from_string(cls, value: Optional[str]) -> "ServerStatus":
        """
        Return the matching enum member, or ServerStatus.NONE
        if the value is None or not recognised.
        """
        if value is None:
            return cls.NONE

        for member in cls:
            if member.value is not None and member.value.casefold() == value.casefold():
                return member

        return cls.NONE
