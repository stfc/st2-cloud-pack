from typing import Optional, List
import logging

from openstack.identity.v3.project import Project

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.runner_utils import RunnerUtils
from openstack_query.runners.runner_wrapper import RunnerWrapper

from custom_types.openstack_query.aliases import ServerSideFilters

logger = logging.getLogger(__name__)


class ProjectRunner(RunnerWrapper):
    """
    Runner class for openstack flavor resource
    ProjectRunner encapsulates running any openstacksdk Project commands
    """

    RESOURCE_TYPE = Project

    def parse_meta_params(self, conn: OpenstackConnection, **kwargs):
        """
        This method is a helper function that will parse a set of meta params specific to the resource and
        return a set of parsed meta-params to pass to _run_query
        """
        logger.debug("ProjectQuery has no meta-params available")
        return super().parse_meta_params(conn, **kwargs)

    def run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[ServerSideFilters] = None,
        **_,
    ) -> List[Project]:
        """
        This method runs the query by running openstacksdk commands

        For ProjectQuery, this command finds all projects that match a given set of filter_kwargs
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional list of filter kwargs to pass to conn.identity.projects()
            to limit the flavors being returned.
            - see https://docs.openstack.org/api-ref/compute/#list-flavors-with-details
        """
        if not filter_kwargs:
            # return all info
            filter_kwargs = {}

        if "id" in filter_kwargs:
            val = conn.identity.find_project(filter_kwargs["id"], ignore_missing=True)
            return [val] if val else []

        logger.debug(
            "running openstacksdk command conn.identity.projects(%s)",
            ",".join(f"{key}={value}" for key, value in filter_kwargs.items()),
        )
        return RunnerUtils.run_paginated_query(
            conn.identity.projects, self._page_marker_prop_func, filter_kwargs
        )
