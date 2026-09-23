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
    status: str
    state: str
    disabled_reason: str
    num_servers: int

    def __init__(self, cloud_account):
        self.cloud_account = cloud_account
        self.conn = openstack.connect(self.cloud_account)

    @staticmethod
    def from_dict(cloud_account: str, dictionary: Dict) -> "Hypervisor":
        """
        Generates a hypervisor object from a dictionary

        :param cloud_account: A string representing the cloud account to use - set in clouds.yaml
        :type cloud_account: str
        :param dictionary: A dictionary containing hypervisor details: hypervisor_name, hypervisor_uptime_days
                           hypervisor_status, hypervisor_state, hypervisor_disabled_reason and hypervisor_server_count
        :type dictionary: Dict

        :return: A hypervisor object with properties from the dictionary
        :rtype: Hypervisor
        """
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
        :type uptime_limit: int

        :return: Hypervisor action
        :rtype: HypervisorAction
        """

        if not self.valid_state():
            return HypervisorAction.NOOP

        if self.state.casefold() == HypervisorState.DOWN.name.casefold():
            logger.info("%s is Down take no action", self.name)
            return HypervisorAction.NOOP  # -> No action if hypervisor is down

        if (
            self.status.casefold() == HypervisorStatus.DISABLED.name.casefold()
            and not self.is_disabled_by_st2()
        ):
            logger.info("%s is manually disabled take no action", self.name)
            return HypervisorAction.NOOP  # -> No action if manually disabled

        # If hypervisor has been up long enough to need maintenance
        if self.uptime > uptime_limit:
            logger.info("%s requires maintenance", self.name)

            # Drained by stackstorm
            if self.should_patch():
                logger.info("%s should be patched", self.name)
                return HypervisorAction.PATCH

            # Disabled by stackstorm or enabled
            if self.can_drain():
                logger.info("%s should be drained", self.name)
                return HypervisorAction.DRAIN  # -> Drain if and capacity

        return HypervisorAction.NOOP

    # pylint:disable=too-many-return-statements
    def valid_state(self) -> bool:
        """
        Validates the hypervisor state

        :param self: The instance of the class

        :return: True for valid state
        :rtype: bool
        """

        if not isinstance(self.name, str):
            return False

        if not isinstance(self.uptime, float):
            return False

        if self.status not in ["enabled", "disabled"]:
            return False

        if self.state not in ["up", "down"]:
            return False

        if not isinstance(self.num_servers, int) or self.num_servers < 0:
            return False

        if self.disabled_reason and not isinstance(self.disabled_reason, str):
            return False

        return True

    def is_disabled_by_st2(self) -> bool:
        """
        Check whether the hypervisor has been diabled by stackstorm
        by checking the disabled reason starts with `Stackstorm:`

        :param self: The instance of the class

        :return: True when disabled by stackstorm
        :rtype: bool
        """
        # TODO: Make this a more robust check, maybe something in netbox
        return self.status.casefold() == HypervisorStatus.DISABLED.name.casefold() and (
            self.disabled_reason.startswith("Stackstorm:")
            if self.disabled_reason
            else False
        )

    def can_drain(self) -> bool:
        """
        Check whether the hypervisor can be drained based on its uptime
        and the percentage of hypervisors disabled in its aggregate

        :param self: The instance of the class

        :return: True when the hypervisor should be drained
        :rtype: bool
        """
        # TODO: Check a tag in netbox for whether the hypervisor is draining or failed to drain
        #       Don't drain if already draining, retry if failed to drain
        return (
            self.status == HypervisorStatus.ENABLED.name or self.is_disabled_by_st2
        ) and self.get_aggregate_capacity() < 0.2

    def should_patch(self) -> bool:
        """
        Check whether the hypervisor should be pacthed based on whether it was
        disabled by st2 and is empty

        :param self: The instance of the class

        :return: True when the hypervisor should be patched
        :rtype: bool
        """
        return self.is_disabled_by_st2() and self.num_servers == 0

    def get_aggregate_capacity(self) -> float:
        """
        Calculates the capacity for the aggregate(s) conatining this hypervisor
        based on the number of hypervisors diabled in the aggregate(s)

        :param self: The instance of the class

        :return: The percentage of hypervisors disabled in the aggregate as a decimal
        :rtype: float
        """

        aggregates = self.conn.compute.aggregates()
        hypervisors = list(self.conn.compute.hypervisors())

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
                lambda hypervisor: hypervisor.name in aggregate.hosts,
                hypervisors,
            )
        )

        # Filter for diabled hypervisors that belong to hypervisor's aggregate
        disabled = list(
            filter(
                lambda hypervisor: hypervisor.status.casefold()
                == HypervisorStatus.DISABLED.name.casefold(),
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
