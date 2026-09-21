from enum import Enum, auto


class HypervisorState(Enum):
    """
    Class of states used for automating maintenace of hypervisors
    """

    RUNNING = auto()
    DOWN = auto()
    DISABLED = auto()
    PENDING_MAINTENANCE = auto()
    START_DRAIN = auto()
    DRAINING = auto()
    DRAINED = auto()
    EMPTY = auto()
    UNKNOWN = auto()

    @classmethod
    def _missing_(cls, value):
        """
        Return UNKNOWN if state not found in class
        """
        return cls.UNKNOWN
