from typing import Dict, List

from apis.openstack_api.enums.hypervisor_states import HypervisorState
from openstack.connection import Connection


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
        hypervisor.name = dictionary["hypervisor_name"]
        hypervisor.uptime = dictionary["hypervisor_uptime_days"]
        hypervisor.status = dictionary["hypervisor_status"]
        hypervisor.state = dictionary["hypervisor_state"]
        hypervisor.disabled_reason = dictionary["hypervisor_disabled_reason"]
        hypervisor.num_servers = dictionary["hypervisor_server_count"]
        return hypervisor

    # pylint:disable=too-many-return-statements
    def get_hypervisor_state(
        self, conn: Connection, uptime_limit: int
    ) -> HypervisorState:
        """
        Returns a hypervisor state given a set of hypervisor variables

        :param uptime_limit: Number of days of uptime before hypervisor requires maintenance
        :return: Hypervisor state
        """
        if self.state == "down":
            return HypervisorState.DOWN

        if self.status == "disabled":
            if not self.is_disabled_by_st2():
                return HypervisorState.DISABLED
            return (
                HypervisorState.DRAINED
                if self.num_servers == 0
                else HypervisorState.DRAINING
            )

        if self.uptime > uptime_limit:
            return (
                HypervisorState.PENDING_MAINTENANCE
                if self.get_aggregate_capacity(conn) > 0.2
                else HypervisorState.START_DRAIN
            )

        if self.status == "enabled":
            return (
                HypervisorState.EMPTY
                if self.num_servers == 0
                else HypervisorState.RUNNING
            )

        return HypervisorState.UNKNOWN

    def is_disabled_by_st2(self) -> bool:
        return self.disabled_reason.startswith("Stackstorm:")

    def get_aggregate_capacity(self, conn: Connection) -> float:
        """
        Calculates the capacity for the aggregate(s) conatining this hypervisor
        based on the number of hypervisors diabled in the aggregate(s)

        :param conn: openstack connection object
        :type conn: Connection
        :param hypervisor_name: Hostname of a hypervisor
        :type hypervisor_name: str
        :return: The percentage of hypervisors disabled as a decimal
        :rtype: float
        """

        aggregates = conn.compute.aggregates()
        hypervisors = list(conn.compute.hypervisors())

        # Find which aggregate(s) the hypervisor belongs to
        aggreates_for_hv = list(
            filter(
                lambda aggregate: self.name in aggregate.hosts,
                aggregates,
            )
        )

        if len(aggreates_for_hv) == 0:
            raise ValueError

        # Get all details for hypervisors in hypervisor's aggregate
        # Assume the first aggregate is a good enough representation of
        # capacity for simplicity.
        # (We only have 2 HVs that are in multiple aggregates)
        aggregate = aggreates_for_hv[0]
        hypervisors = list(
            filter(
                lambda self: self.name in aggregate.hosts,
                hypervisors,
            )
        )

        # Filter for diabled hypervisors that belong to hypervisor's aggregate
        disabled = list(
            filter(
                lambda hypervisor: hypervisor.status == "disabled",
                hypervisors,
            )
        )

        return len(disabled) / len(hypervisors)


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
