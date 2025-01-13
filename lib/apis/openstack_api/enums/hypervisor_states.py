from enum import Enum, auto


class HypervisorState(Enum):
    """
    Class of states used for automating maintenace of hypervisors
    """

    RUNNING = auto()
    PENDING_MAINTENANCE = auto()
    DRAINING = auto()
    DRAINED = auto()
    UNKNOWN = auto()
    REBOOTED = auto()
    EMPTY = auto()
    DOWN = auto()

    @classmethod
    def _missing_(cls, value):
        """
        Return UNKNOWN if state not found in class
        """
        return cls.UNKNOWN
