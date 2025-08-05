from typing import Dict, List

from apis.openstack_api.enums.hypervisor_states import HypervisorState
from openstack.connection import Connection


def get_hypervisor_state(hypervisor: Dict, uptime_limit: int) -> HypervisorState:
    """
    Returns a hypervisor state given a set of hypervisor variables
    :param hypervisor: Dictionary containing hypervisor: uptime, state, status and server count
    :param uptime_limit: Number of days of uptime before hypervisor requires maintenance
    :return: Hypervisor state
    """
    if hypervisor["hypervisor_state"] == "down":
        return HypervisorState.DOWN
    if hypervisor["hypervisor_disabled_reason"] and not hypervisor[
        "hypervisor_disabled_reason"
    ].startswith("Stackstorm:"):
        return HypervisorState.DISABLED
    if not valid_state(hypervisor):
        return HypervisorState.UNKNOWN
    if (
        hypervisor["hypervisor_uptime_days"] >= uptime_limit
        and hypervisor["hypervisor_status"] == "enabled"
    ):
        return HypervisorState.PENDING_MAINTENANCE
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
    if not isinstance(state["hypervisor_uptime_days"], float):
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


def get_available_flavors(conn: Connection, hypervisor_name: str) -> List[str]:
    """
    Returns names of flavors which can be built on a given hypervisor
    :param conn: openstack connection object
    :type conn: Connection
    :param hypervisor_name: Hostname of a hypervisor
    :type hypervisor_name: str
    :return: List of flavor names
    :rtype: List[str]
    """
    available_flavors = []
    for agg in conn.compute.aggregates():
        hosttype = agg.metadata.get("hosttype")
        local_storage_type = agg.metadata.get("local-storage-type")

        if hypervisor_name in agg.hosts:
            for flavor in conn.compute.flavors(
                extra_specs={
                    "aggregate_instance_extra_specs:hosttype": hosttype,
                    "aggregate_instance_extra_specs:local-storage-type": local_storage_type,
                }
            ):
                available_flavors.append(flavor.name)

    return available_flavors
