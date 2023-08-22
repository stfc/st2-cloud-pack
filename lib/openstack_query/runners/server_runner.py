from typing import Optional, List, Dict
import logging

from openstack.compute.v2.server import Server

from openstack.exceptions import ResourceNotFound

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.query_runner import QueryRunner

from exceptions.parse_query_error import ParseQueryError
from custom_types.openstack_query.aliases import (
    ProjectIdentifier,
    ServerSideFilters,
)


logger = logging.getLogger(__name__)

# pylint:disable=too-few-public-methods


class ServerRunner(QueryRunner):
    """
    Runner class for openstack Server resource.
    ServerRunner encapsulates running any openstacksdk Server commands
    """

    def _parse_meta_params(
        self,
        conn: OpenstackConnection,
        from_projects: Optional[List[ProjectIdentifier]] = None,
    ) -> Dict:
        """
        This method is a helper function that will parse a set of query meta params related to openstack server queries.
        :param conn: An OpenstackConnection object - used to connect to openstack and parse meta params
        """
        project_list = []
        for proj in from_projects:
            try:
                logger.debug(
                    "running conn.identity.find_project(%s, ignore_missing=False)", proj
                )
                project = conn.identity.find_project(proj, ignore_missing=False)["id"]
            except ResourceNotFound as exp:
                raise ParseQueryError(
                    "Failed to execute query: Failed to parse meta params"
                ) from exp
            project_list.append(project)
        if project_list:
            return {"projects": project_list}
        return {}

    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[ServerSideFilters] = None,
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

        # so we can search in all projects instead of default set in clouds.yaml
        filter_kwargs.update({"all_tenants": True})

        if not meta_params["projects"]:
            logger.debug("running query on all projects")
            logger.debug(
                "running openstacksdk command conn.compute.servers (%s)",
                ",".join(f"{key}={value}" for key, value in filter_kwargs.items()),
            )
            return self._run_paginated_query(conn.compute.servers, filter_kwargs)

        if "project_id" in filter_kwargs.keys():
            raise ParseQueryError(
                "This query uses a preset that requires searching on project_ids "
                "- but you've provided projects to search in using from_projects meta param"
                "- please use one or the other, not both"
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
                ",".join(f"{key}={value}" for key, value in filter_kwargs.items()),
            )
            query_res.extend(
                self._run_paginated_query(conn.compute.servers, filter_kwargs)
            )
        return query_res

    def _parse_subset(
        self, _: OpenstackConnection, subset: List[Server]
    ) -> List[Server]:
        """
        This method is a helper function that will check a list of servers to ensure that they are valid Server
        objects
        :param subset: A list of openstack Server objects
        """

        # should check validity that each server still exists but takes too long
        if any(not isinstance(i, Server) for i in subset):
            raise ParseQueryError("'from_subset' only accepts Server openstack objects")
        return subset
