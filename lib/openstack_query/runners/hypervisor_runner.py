import logging
from typing import Optional, List

from custom_types.openstack_query.aliases import ServerSideFilters, OpenstackResourceObj
from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.runner_utils import RunnerUtils
from openstack_query.runners.runner_wrapper import RunnerWrapper
from openstack.compute.v2.hypervisor import Hypervisor

logger = logging.getLogger(__name__)


class HypervisorRunner(RunnerWrapper):
    """
    Runner class for openstack Hypervisor resource
    HypervisorRunner encapsulates running any openstacksdk Hypervisor commands
    """

    RESOURCE_TYPE = Hypervisor

    def parse_meta_params(self, conn: OpenstackConnection, **kwargs):
        """
        This method is a helper function that will parse a set of meta params specific to the resource and
        return a set of parsed meta-params to pass to _run_query
        """
        logger.debug("HypervisorQuery has no meta-params available")
        return super().parse_meta_params(conn, **kwargs)

    # pylint: disable=unused-argument
    def run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[ServerSideFilters] = None,
        **kwargs,
    ) -> List[OpenstackResourceObj]:
        """
        This method runs the query by running openstacksdk commands

        For HypervisorQuery, this command finds all hypervisors that match a given set of filter_kwargs
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional list of filter kwargs to pass to conn.compute.hypervisors()
            to limit the hypervisors being returned.
            - see https://docs.openstack.org/api-ref/compute/?expanded=list-hypervisors-detail
        """
        if not filter_kwargs:
            # return server info
            filter_kwargs = {"details": True}
        logger.debug(
            "running openstacksdk command conn.compute.hypervisors(%s)",
            ",".join(f"{key}={value}" for key, value in filter_kwargs.items()),
        )
        return RunnerUtils.run_paginated_query(
            conn.compute.hypervisors, self._page_marker_prop_func, filter_kwargs
        )
