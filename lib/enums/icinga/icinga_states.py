from enum import Enum


class HostState(Enum):
    """
    Mapping value to Host state, https://icinga.com/docs/icinga-2/latest/doc/03-monitoring-basics/#host-states
    """

    UP = 0
    DOWN = 1


class ServiceState(Enum):
    """
    Mapping value to Service state, https://icinga.com/docs/icinga-2/latest/doc/03-monitoring-basics/#service-states
    """

    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKOWN = 3
