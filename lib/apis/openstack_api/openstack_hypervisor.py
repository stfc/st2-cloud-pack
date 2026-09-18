from typing import Dict, List

from apis.openstack_api.enums.hypervisor_states import HypervisorState


class Hypervisor:
    name: str
    uptime: int
    status: bool
    state: bool
    disabled_reason: str
    num_servers: int

    @staticmethod
    def from_dict(dictionary: Dict):
        hypervisor = Hypervisor()
        hypervisor.uptime = dictionary["hypervisor_uptime_days"]
        hypervisor.status = dictionary["hypervisor_status"]
        hypervisor.state = dictionary["hypervisor_state"]
        hypervisor.disabled_reason = dictionary["hypervisor_disabled_reason"]
        hypervisor.num_servers = dictionary["hypervisor_server_count"]
        return hypervisor

    def get_hypervisor_state(self, uptime_limit: int) -> HypervisorState:
        """
        Returns a hypervisor state given a set of hypervisor variables
        :param hypervisor: Dictionary containing hypervisor: uptime, state, status and server count
        :param uptime_limit: Number of days of uptime before hypervisor requires maintenance
        :return: Hypervisor state
        """
        if self.state == "down":
            return HypervisorState.DOWN

        if self.uptime == 0:
            return HypervisorState.REBOOTED

        if self.status == "disabled":
            if not self.is_disabled_by_st2():
                return HypervisorState.DISABLED
            return (
                HypervisorState.DRAINED
                if self.num_servers == 0
                else HypervisorState.DRAINING
            )

        if self.uptime > uptime_limit:
            return HypervisorState.PENDING_MAINTENANCE

        if self.status == "enabled":
            return (
                HypervisorState.EMPTY
                if self.num_servers == 0
                else HypervisorState.RUNNING
            )

        return HypervisorState.UNKNOWN

    def is_disabled_by_st2(self) -> bool:
        return self.disabled_reason.startswith("Stackstorm:")


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
