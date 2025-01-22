from typing import Dict
from enums.hypervisor_states import HypervisorState


def get_hypervisor_state(hypervisor: Dict, uptime_limit: int) -> HypervisorState:
    """
    Returns a hypervisor state given a set of hypervisor variables
    :param hypervisor: Dictionary containing hypervisor: uptime, state, status and server count
    :param uptime_limit: Number of days of uptime before hypervisor requires maintenance
    :return: Hypervisor state
    """
    if hypervisor["hypervisor_state"] == "down":
        return HypervisorState.DOWN
    if not valid_state(hypervisor):
        return HypervisorState.UNKNOWN
    hv_state = {
        "uptime": hypervisor["hypervisor_uptime_days"] < uptime_limit,
        "enabled": hypervisor["hypervisor_status"] == "enabled",
        "state": hypervisor["hypervisor_state"] == "up",
        "servers": hypervisor["hypervisor_server_count"] > 0,
    }

    return HypervisorState(hv_state)


def valid_state(state) -> bool:
    """
    Validates the hypervisor state
    :param state: Dictionary containing hypervisor state
    :return: True for valid state
    """
    if not isinstance(state["hypervisor_uptime_days"], int):
        return False
    hypervisor_status = state["hypervisor_status"]
    if hypervisor_status not in ["enabled", "disabled"]:
        return False
    hypervisor_state = state["hypervisor_state"]
    if hypervisor_state not in ["up", "down"]:
        return False
    hypervisor_server_count = state["hypervisor_server_count"]
    if not isinstance(hypervisor_server_count, int) or hypervisor_server_count < 0:
        return False
    return True
