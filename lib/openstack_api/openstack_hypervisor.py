import re
from typing import Dict
from enums.hypervisor_states import HypervisorState


def get_hypervisor_state(hypervisor: Dict, uptime_limit: int) -> str:
    """
    Returns a hypervisor state given a set of hypervisor variables
    :param hypervisor: Dictionary containing hypervisor: uptime, state, status and server count
    :param uptime_limit: Number of days of uptime before hypervisor requires maintenance
    :return: Hypervisor state
    """
    uptime_pattern = re.compile(r"up\s+(\d+)\s+days,?\s+(\d+):(\d+)")
    hypervisor_uptime = hypervisor.get("hypervisor_uptime")

    if not (
        isinstance(hypervisor_uptime, str)
        and (match := uptime_pattern.search(hypervisor_uptime))
    ):
        return "UNKNOWN"

    hypervisor_status = hypervisor.get("hypervisor_status")
    if hypervisor_status not in ["enabled", "disabled"]:
        return "UNKNOWN"

    hypervisor_state = hypervisor.get("hypervisor_state")
    if hypervisor_state not in ["up", "down"]:
        return "UNKNOWN"

    hypervisor_server_count = hypervisor.get("hypervisor_server_count")
    if not isinstance(hypervisor_server_count, int) or hypervisor_server_count < 0:
        return "UNKNOWN"

    days = int(match.group(1))
    hv_state = {
        "uptime": days < uptime_limit,
        "enabled": hypervisor_status == "enabled",
        "state": hypervisor_state == "up",
        "servers": hypervisor_server_count > 0,
    }

    for state in HypervisorState:
        if state.properties() == hv_state:
            return state.name

    return "UNKNOWN"
