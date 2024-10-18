from enum import Enum, auto


class HypervisorState(Enum):
    """
    Class of states used for automating maintenace of hypervisors
    """

    RUNNING = auto()
    PENDING_MAINTENANCE = auto()
    DRAINING = auto()
    DRAINED = auto()

    def properties(self):
        """
        Return hypervisor state for given variables
        """
        state_properties = {
            HypervisorState.RUNNING: {
                "uptime": True,
                "enabled": True,
                "state": True,
                "servers": True,
            },
            HypervisorState.PENDING_MAINTENANCE: {
                "uptime": False,
                "enabled": True,
                "state": True,
                "servers": True,
            },
            HypervisorState.DRAINING: {
                "uptime": False,
                "enabled": False,
                "state": True,
                "servers": True,
            },
            HypervisorState.DRAINED: {
                "uptime": False,
                "enabled": False,
                "state": True,
                "servers": False,
            },
        }
        return state_properties[self]
