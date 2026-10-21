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

    @classmethod
    def from_string(cls, value: str) -> Optional["ServerStatus"]:
        """
        Return the enum member matching the given status string,
        or None when the status is not tracked

        :param value: the status string returned by the OpenStack API
        :return: the matching ServerStatus member, or None
        """
        value = value.casefold()
        for member in cls:
            if member.value.casefold() == value:
                return member
        return None
