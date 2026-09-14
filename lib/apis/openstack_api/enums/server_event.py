from enum import Enum
from typing import Optional


class ServerEvent(Enum):
    """
    Maps to events tracked in a server event list.
    Only contains the events we currently use
    """

    START = "start"
    STOP = "stop"
    SHELVE = "shelve"
    UNSHELVE = "unshelve"
    SHELVE_OFFLOAD = "shelveOffload"

    @classmethod
    def from_string(cls, value: str) -> Optional["ServerEvent"]:
        """
        Return the event enum or None
        if the event is not tracked

        :param value: the event name returned by OpenStack
        :return: the matching ServerEvent member, or None
        """
        value = value.casefold()
        for member in cls:
            if member.value.casefold() == value:
                return member
        return None
