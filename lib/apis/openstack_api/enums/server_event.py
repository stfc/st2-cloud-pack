from enum import Enum


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
    UNKNOWN = "unknown"  # For events we don't currently track

    @classmethod
    def from_string(cls, value: str) -> "ServerEvent":
        """
        Return the event enum or UNKNOWN
        if the event is not something we track currently

        :param value: the event name returned by OpenStack
        :return: the matching ServerEvent member, or None
        """
        value = value.casefold()
        for member in cls:
            if member.value.casefold() == value:
                return member
        return cls.UNKNOWN
