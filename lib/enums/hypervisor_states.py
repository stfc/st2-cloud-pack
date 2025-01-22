from enum import Enum, auto


class HypervisorState(Enum):
    """
    Class of states used for automating maintenace of hypervisors
    """

    RUNNING = {
        "uptime": True,
        "enabled": True,
        "state": True,
        "servers": True,
    }
    PENDING_MAINTENANCE = {
        "uptime": False,
        "enabled": True,
        "state": True,
        "servers": True,
    }
    DRAINING = {
        "uptime": False,
        "enabled": False,
        "state": True,
        "servers": True,
    }
    DRAINED = {
        "uptime": False,
        "enabled": False,
        "state": True,
        "servers": False,
    }
    REBOOTED = {
        "uptime": True,
        "enabled": False,
        "state": True,
        "servers": False,
    }
    EMPTY = {
        "uptime": True,
        "enabled": True,
        "state": True,
        "servers": False,
    }
    DOWN = auto()
    UNKNOWN = auto()

    @classmethod
    def _missing_(cls, value):
        """
        Return UNKNOWN if state not found in class
        """
        return cls.UNKNOWN
