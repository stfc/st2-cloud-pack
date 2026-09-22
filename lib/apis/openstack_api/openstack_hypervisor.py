import logging
from typing import Dict, List

import openstack

from apis.openstack_api.enums.hypervisor_enums import (
    HypervisorAction,
    HypervisorState,
    HypervisorStatus,
)
from openstack.connection import Connection

logger = logging.getLogger(__name__)


# pylint:disable=too-many-instance-attributes
class Hypervisor:
    name: str
    uptime: int
    status: bool
    state: bool
    disabled_reason: str
    num_servers: int

    def __init__(self, cloud_account):
        self.cloud_account = cloud_account
        self.conn = openstack.connect(self.cloud_account)

    @staticmethod
    def from_dict(cloud_account: str, dictionary: Dict):
        hypervisor = Hypervisor(cloud_account)
        hypervisor.name = dictionary["hypervisor_name"]
        hypervisor.uptime = dictionary["hypervisor_uptime_days"]
        hypervisor.status = dictionary["hypervisor_status"]
        hypervisor.state = dictionary["hypervisor_state"]
        hypervisor.disabled_reason = dictionary["hypervisor_disabled_reason"]
        hypervisor.num_servers = dictionary["hypervisor_server_count"]
        return hypervisor

    def take_action(self, uptime_limit: int) -> HypervisorAction:
        """
        Returns a hypervisor action based on certain conditions

        :param uptime_limit: Number of days of uptime before hypervisor requires maintenance
        :return: Hypervisor state
        """

        if self.state == HypervisorState.DOWN:
            logger.info("%s is Down take no action", self.name)
            return HypervisorAction.NOOP  # -> No action if hypervisor is down

        if self.status == HypervisorStatus.DISABLED and not self.is_disabled_by_st2():
            logger.info("%s is manually disabled take no action", self.name)
            return HypervisorAction.NOOP  # -> No action if manually disabled

        # If hypervisor has been up long enough to need maintenance
        if self.uptime > uptime_limit:
            logger.info("%s requires maintenance", self.name)

            # Disabled by stackstorm or enabled
            if self.should_drain(self.conn):
                logger.info("%s should be drained", self.name)
                return HypervisorAction.DRAIN  # -> Drain if and capacity

            # Drained by stackstorm
            if self.should_patch():
                logger.info("%s should be patched", self.name)
                return HypervisorAction.PATCH

        return HypervisorAction.NOOP

    def is_disabled_by_st2(self) -> bool:
        """
        Check whether the hypervisor has been diabled by stackstorm
        by checking the disabled reason starts with `Stackstorm:`

        :rtype: bool
        """
        # TODO: Make this a more robust check, maybe something in netbox
        return (
            self.status == HypervisorStatus.DISABLED
            and self.disabled_reason.startswith("Stackstorm:")
        )

    def should_drain(self, conn: Connection) -> bool:
        """
        Check whether the hypervisor should be drained based on its uptime
        and the percentage of hypervisors disabled in its aggregate

        :param uptime_limit: Number of days of uptime before hypervisor requires maintenance
                             for maintenance
        :rtype: bool
        """
        # TODO: Check a tag in netbox for whether the hypervisor is draining or failed to drain
        #       Don't drain if already draining, retry if failed to drain
        return (
            self.status == HypervisorStatus.ENABLED or self.is_disabled_by_st2
        ) and self.get_aggregate_capacity(conn) < 0.2

    def should_patch(self) -> bool:
        """
        Check whether the hypervisor should be pacthed based on whether it was
        disabled by st2 and is empty

        :param self: Description
        :return: Description
        :rtype: bool
        """
        return self.is_disabled_by_st2() and self.num_servers == 0

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
