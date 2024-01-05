from typing import Optional, List, Dict
import logging

from openstack.compute.v2.server import Server

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.runner_utils import RunnerUtils
from openstack_query.runners.runner_wrapper import RunnerWrapper

from exceptions.parse_query_error import ParseQueryError
from custom_types.openstack_query.aliases import (
    ProjectIdentifier,
    ServerSideFilter,
)

logger = logging.getLogger(__name__)


class ServerRunner(RunnerWrapper):
    """
    Runner class for openstack Server resource.
    ServerRunner encapsulates running any openstacksdk Server commands
    """

    RESOURCE_TYPE = Server

    def parse_meta_params(
        self,
        conn: OpenstackConnection,
        from_projects: Optional[List[ProjectIdentifier]] = None,
        all_projects: bool = False,
        as_admin: bool = False,
    ) -> Dict:
        """
        This method is a helper function that will parse a set of query meta params related to openstack server queries.
        :param conn: An OpenstackConnection object - used to connect to openstack and parse meta params
        :param from_projects: A list of projects to search in
        :param all_projects: A boolean which, if true - will run query on all available projects to the user
        :param as_admin: A boolean which, if true - will run query as an admin
        """

        # raise error if ambiguous query
        if from_projects and all_projects:
            raise ParseQueryError(
                "Failed to execute query: ambiguous run params - run with either "
                "from_projects or all_projects and not both"
            )

        if not as_admin and (all_projects or from_projects):
            raise ParseQueryError(
                "Failed to execute query: all_projects and/or from_project run_params won't work if"
                "you're not running as admin"
            )

        # don't provide any projects to scope the query so it runs on all projects
        if all_projects:
            return {"all_tenants": True}

        if not from_projects:
            logger.warning(
                "Query will only work on the scoped project id: %s",
                conn.current_project_id,
            )
            from_projects = [conn.current_project_id]

        projects = RunnerUtils.parse_projects(conn, from_projects)

        # all_tenants only works if admin
        if not as_admin:
            return {"projects": projects}
        return {"all_tenants": True, "projects": projects}

    def run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[ServerSideFilter] = None,
        **meta_params,
    ) -> List[Server]:
        """
        This method runs the query by running openstacksdk commands

        For ServerQuery, this command gets all projects available and iteratively finds servers that belong to that
        project
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional set of filter kwargs to pass to conn.compute.servers()
            to limit the servers being returned. - see https://docs.openstack.org/api-ref/compute/#list-servers
        :param meta_params: a set of meta parameters that dictates how the query is run
        """
        if not filter_kwargs:
            filter_kwargs = {}

        if "project_id" in filter_kwargs.keys() and "projects" in meta_params:
            raise ParseQueryError(
                "This query uses a preset that requires searching on project_ids "
                "- but you've provided projects to search in using from_projects meta param"
                "- please use one or the other, not both"
                "- or you are not running as admin"
            )

        if "all_tenants" in meta_params:
            filter_kwargs["all_tenants"] = meta_params["all_tenants"]

        if "projects" not in meta_params:
            logger.debug(
                "running openstacksdk command conn.compute.servers (%s)",
                ", ".join(f"{key}={value}" for key, value in filter_kwargs.items()),
            )
            return RunnerUtils.run_paginated_query(
                conn.compute.servers, self._page_marker_prop_func, dict(filter_kwargs)
            )

        query_res = []
        project_num = len(meta_params["projects"])
        logger.debug("running query on %s projects", project_num)
        for i, project_id in enumerate(meta_params["projects"], 1):
            filter_kwargs.update({"project_id": project_id})
            logger.debug(
                "running query on project %s / %s (id: %s)", i, project_num, project_id
            )
            logger.debug(
                "running openstacksdk command conn.compute.servers (%s)",
                ", ".join(f"{key}={value}" for key, value in filter_kwargs.items()),
            )
            query_res.extend(
                RunnerUtils.run_paginated_query(
                    conn.compute.servers,
                    self._page_marker_prop_func,
                    dict(filter_kwargs),
                )
            )
        return query_res
