from enum import Enum, auto


class HypervisorAction(Enum):
    """
    Class of actions used for automating maintenace of hypervisors
    """

    NOOP = auto()
    DRAIN = auto()
    PATCH = auto()

    @classmethod
    def _missing_(cls, value):
        """
        Return UNKNOWN if state not found in class
        """
        return cls.NOOP


class HypervisorState(Enum):
    """
    Class of hypervisors states
    """

    UP = auto()
    DOWN = auto()


class HypervisorStatus(Enum):
    """
    Class of hypervisors statuses
    """

    ENABLED = auto()
    DISABLED = auto()


class HypervisorOS(Enum):
    """
    Class of hypervisors operating systems, using IDs from netbox
    https://netbox.esc.rl.ac.uk/dcim/platforms/
    """

    ROCKY_8 = 14
    ROCKY_9 = 15
    ROCKY_10 = 36
