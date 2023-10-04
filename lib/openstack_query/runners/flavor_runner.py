from typing import Optional, List
import logging

from openstack.compute.v2.flavor import Flavor
from exceptions.parse_query_error import ParseQueryError

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.runner_wrapper import RunnerWrapper

from custom_types.openstack_query.aliases import ServerSideFilters

logger = logging.getLogger(__name__)

# pylint:disable=too-few-public-methods


class FlavorRunner(RunnerWrapper):
    """
    Runner class for openstack flavor resource
    FlavorRunner encapsulates running any openstacksdk Flavor commands
    """

    def _parse_meta_params(self, _: OpenstackConnection, **__):
        logger.error(
            "FlavorQuery doesn't take any meta-params, if you think it should,"
            "please raise an issue with the repo maintainers"
        )
        raise ParseQueryError("FlavorQuery has no meta-params available")

    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[ServerSideFilters] = None,
        **_,
    ) -> List[Flavor]:
        """
        This method runs the query by running openstacksdk commands

        For FlavorQuery, this command finds all flavors that match a given set of filter_kwargs
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional list of filter kwargs to pass to conn.compute.flavors()
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
        return self._run_paginated_query(conn.compute.flavors, filter_kwargs)

    def _parse_subset(
        self, _: OpenstackConnection, subset: List[Flavor]
    ) -> List[Flavor]:
        """
        This method is a helper function that will check a list of flavors to ensure that they are valid Flavor
        objects
        :param subset: A list of openstack Flavor objects
        """

        # should check validity that each flavor still exists but takes too long
        if any(not isinstance(i, Flavor) for i in subset):
            raise ParseQueryError("'from_subset' only accepts Flavor openstack objects")
        return subset
