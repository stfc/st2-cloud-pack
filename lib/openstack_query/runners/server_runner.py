from typing import Optional, Dict, List

from openstack.compute.v2.server import Server
from openstack.identity.v3.project import Project

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.query_runner import QueryRunner

from exceptions.parse_query_error import ParseQueryError


class ServerRunner(QueryRunner):
    """
    Runner class for openstack Server resource.
    ServerRunner encapsulates running any openstacksdk Server commands
    """

    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> List[Server]:
        """
        This method runs the query by running openstacksdk commands

        For QueryServer, this command gets all projects available and iteratively finds servers that belong to that project
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional set of filter kwargs to pass to conn.compute.servers()
            to limit the servers being returned. - see https://docs.openstack.org/api-ref/compute/#list-servers

        :param kwargs: a set of extra meta params that override default openstacksdk command. Current valid kwargs are:

            'from_projects': Union[List[str], List[Project]] - takes a list of projects to run the query on

            'from_subset': Union[List[str], List[Server]] - takes a list of servers to run the query on
            (forces use of filter functions)

        """
        projects = []
        if "from_projects" in kwargs:
            if len(kwargs["from_projects"]) == 0:
                raise ParseQueryError(
                    "'from_project' meta kwarg given but no projects given to search in"
                )
            for project in kwargs["from_projects"]:
                if not isinstance(project, Project):
                    raise ParseQueryError(
                        "'from_project' only accepts Openstack 'Project' objects"
                    )
                projects.append(project)
        else:
            for project in conn.identity.projects():
                projects.append(project)

        return self._run_query_on_projects(conn, projects, filter_kwargs)

    def _run_query_on_projects(
        self,
        conn: OpenstackConnection,
        projects: List[Project],
        filter_kwargs: Optional[Dict[str, str]] = None,
    ) -> List[Server]:
        """
        This method is a helper function that will run the query on a list of openstack projects given
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param projects: A list of openstacksdk projects to run query on
        :param filter_kwargs: An Optional set of filter kwargs to pass to conn.compute.servers()
        """
        return [
            server
            for project in projects
            for server in self._run_query_on_project(conn, project, filter_kwargs)
        ]

    @staticmethod
    def _run_query_on_project(
        conn: OpenstackConnection,
        project: Project,
        filter_kwargs: Optional[Dict[str, str]] = None,
    ) -> List[Server]:
        """
        This method is a helper function that will list all servers that belong to a given openstack projects
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param project: An openstacksdk project to run query on
        :param filter_kwargs: An Optional set of filter kwargs to pass to conn.compute.servers()
        """
        server_filters = {"project_id": project["id"], "all_tenants": True}
        server_filters.update(filter_kwargs if filter_kwargs else {})
        return list(conn.compute.servers(filters=server_filters))

    def _parse_subset(
        self, conn: OpenstackConnection, subset: List[Server]
    ) -> List[Server]:
        """
        This method is a helper function that will check a list of servers to ensure that they are valid Server objects
        :param subset: A list of openstack Server objects
        """
        for server in subset:
            if not isinstance(server, Server):
                raise ParseQueryError(
                    "'from_subset' only accepts Server openstack objects"
                )
        return subset
