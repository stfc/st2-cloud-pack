import datetime as dt
import logging
from dataclasses import dataclass
from typing import Dict, List, Sequence

import openstack
from apis.netbox_api.device import get_fw_patch_date, get_platform
from apis.openstack_api.enums.hypervisor_enums import (
    HypervisorAction,
    HypervisorState,
    HypervisorStatus,
)
from apis.utils.weighers import get_weights
from openstack.connection import Connection

logger = logging.getLogger(__name__)


# pylint:disable=too-many-instance-attributes
@dataclass
class Hypervisor:
    name: str
    uptime_days: float
    status: HypervisorStatus
    state: HypervisorState
    disabled_reason: str | None
    hypervisor_server_count: int

    MAX_DISABLED_PERCENTAGE_CAPACITY_IN_AGGREGATE = 0.2  # Max 20% disabled
    TARGET_OS_VERSION = 9

    def __init__(self, cloud_account):
        self.cloud_account = cloud_account
        self.conn = openstack.connect(self.cloud_account)

        self._previous_fw_patch_date: str | None = None
        self._os_version: int | None = None

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
        if not isinstance(dictionary["hypervisor_name"], str):
            raise ValueError(
                f'Invalid hypervisor name: {dictionary["hypervisor_name"]}'
            )
        hypervisor.name = dictionary["hypervisor_name"]

        hypervisor.uptime_days = int(dictionary["hypervisor_uptime_days"])

        status = dictionary["hypervisor_status"]
        hypervisor.status = HypervisorStatus[str(status).upper()]

        state = dictionary["hypervisor_state"]
        hypervisor.state = HypervisorState[str(state).upper()]

        if dictionary["hypervisor_disabled_reason"] and not isinstance(
            dictionary["hypervisor_disabled_reason"], str
        ):
            raise ValueError(
                f'Invalid disabled reason: {dictionary["hypervisor_disabled_reason"]}'
            )
        hypervisor.disabled_reason = dictionary["hypervisor_disabled_reason"]

        if dictionary["hypervisor_server_count"] < 0:
            raise ValueError(
                f'{dictionary["hypervisor_name"]} has a negative server count'
            )
        hypervisor.hypervisor_server_count = int(dictionary["hypervisor_server_count"])

        return hypervisor

    def take_action(self, uptime_limit: int) -> HypervisorAction:
        """
        Returns a hypervisor action based on certain conditions

        :param uptime_limit: Number of days of uptime before hypervisor requires maintenance
        :type uptime_limit: int

        :return: Hypervisor action
        :rtype: HypervisorAction
        """

        if self.state == HypervisorState.DOWN:
            logger.info("%s is Down take no action", self.name)
            return HypervisorAction.NOOP  # -> No action if hypervisor is down

        if self.status == HypervisorStatus.DISABLED and not self.is_disabled_by_st2():
            logger.info("%s is manually disabled take no action", self.name)
            return HypervisorAction.NOOP  # -> No action if manually disabled

        # If hypervisor has been up long enough to need maintenance
        if self.uptime_days > uptime_limit:
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

    def is_disabled_by_st2(self) -> bool:
        """
        Check whether the hypervisor has been diabled by stackstorm
        by checking the disabled reason starts with `Stackstorm:`

        :param self: The instance of the class

        :return: True when disabled by stackstorm
        :rtype: bool
        """
        # TODO: Make this a more robust check, maybe something in netbox
        return self.status == HypervisorStatus.DISABLED and (
            self.disabled_reason.startswith("Stackstorm:")
            if self.disabled_reason
            else False
        )

    def can_drain(self) -> bool:
        """
        Check whether the hypervisor can be drained based on
        the percentage of hypervisors disabled in its aggregate
        or if its already disabled for draining

        :param self: The instance of the class

        :return: True when the hypervisor should be drained
        :rtype: bool
        """
        # TODO: Check a tag in netbox for whether the hypervisor is draining or failed to drain
        #       Don't drain if already draining, retry if failed to drain
        return (
            self.get_aggregate_capacity()
            < self.MAX_DISABLED_PERCENTAGE_CAPACITY_IN_AGGREGATE
            and self.status == HypervisorStatus.ENABLED
        ) or self.is_disabled_by_st2()

    def should_patch(self) -> bool:
        """
        Check whether the hypervisor should be pacthed based on whether it was
        disabled by st2 and is empty

        :param self: The instance of the class

        :return: True when the hypervisor should be patched
        :rtype: bool
        """
        return self.is_disabled_by_st2() and self.hypervisor_server_count == 0

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

    @property
    def os_version(self) -> int:
        if self._os_version is None:
            self._os_version = get_platform()
        return self._os_version

    @property
    def previous_fw_patch_date(self) -> str:
        if self._previous_fw_patch_date is None:
            self._previous_fw_patch_date = get_fw_patch_date()
        return self._previous_fw_patch_date

    def hypervisor_server_count_metric(self) -> int:
        """
        Favour hypervisors with fewer VMs on

        :param hypervisor_server_count: Number of servers on the hypervisor
        :type hypervisor_server_count: int

        :return: Server count metric
        :rtype: int
        """
        return -self.hypervisor_server_count

    def last_fw_patch_date_metric(self) -> int:
        """
        Prioritise hosts with longer FW patch date duration

        :param patch_date: Date of the last FW patch date
        :type patch_date: str

        :return: FW patch date metric
        :rtype: int
        """
        date = dt.datetime.strptime(self.previous_fw_patch_date, "%Y-%m-%d")
        return (dt.datetime.now() - date).days

    def os_version_metric(self) -> bool:
        """
        Deprioritse hosts currently runing the target version
        of the operating system

        :return: OS version metric
        :rtype: bool
        """
        return self.os_version != self.TARGET_OS_VERSION

    @property
    def maint_score(self) -> float:
        """
        Calculates the score for a host based on property metrics
        To sort them into priority order

        score = (m1 * w1) + (m2 * w2) + ...

        :param host: Dictionary containing properties of the host to weigh
        :type host: dict
        :param weights: Multipliers for the properties to (de)priorities their importance
        :type weights: dict

        :return: Host priority weight
        :rtype: float
        """
        weights = get_weights()
        score = 0

        for metric, mult in weights.items():
            try:
                metric_fn = getattr(self, f"{metric}_metric")
            except AttributeError as exc:
                raise AttributeError() from exc

            value = metric_fn()

            score += value * mult

        return score


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


def prioritse_patching(hosts: List[Hypervisor]) -> Sequence[Hypervisor]:
    """
    Prioritises a list of hyperviosrs to order them by priority of patching

    :param hosts: List of hypervisors
    :type hosts: Sequence[dict]

    :return: An ordered list of hypervisors by the priority of patching
    :rtype:  List[dict]
    """

    return sorted(hosts, key=lambda x: x.maint_score, reverse=True)
