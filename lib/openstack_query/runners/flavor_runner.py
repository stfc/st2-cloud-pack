from typing import Optional, List
import logging

from openstack.compute.v2.flavor import Flavor
from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.runner_wrapper import RunnerWrapper
from openstack_query.runners.runner_utils import RunnerUtils

from custom_types.openstack_query.aliases import ServerSideFilter

logger = logging.getLogger(__name__)


class FlavorRunner(RunnerWrapper):
    """
    Runner class for openstack flavor resource
    FlavorRunner encapsulates running any openstacksdk Flavor commands
    """

    RESOURCE_TYPE = Flavor

    def parse_meta_params(self, conn: OpenstackConnection, **kwargs):
        """
        This method is a helper function that will parse a set of meta params specific to the resource and
        return a set of parsed meta-params to pass to _run_query
        """
        logger.debug("FlavorQuery has no meta-params available")
        return super().parse_meta_params(conn, **kwargs)

    def run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[ServerSideFilter] = None,
        **_,
    ) -> List[Flavor]:
        """
        This method runs the query by running openstacksdk commands

        For FlavorQuery, this command finds all flavors that match a given set of filter_kwargs
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional set of filter kwargs to pass to conn.compute.flavors()
            to limit the flavors being returned.
            - see https://docs.openstack.org/api-ref/compute/#list-flavors-with-details
        """
        if not filter_kwargs:
            # return all info
            filter_kwargs = {"details": True}
        logger.debug(
            "running openstacksdk command conn.compute.flavors(%s)",
            ",".join(f"{key}={value}" for key, value in filter_kwargs.items()),
        )
        return RunnerUtils.run_paginated_query(
            conn.compute.flavors, self._page_marker_prop_func, filter_kwargs
        )
