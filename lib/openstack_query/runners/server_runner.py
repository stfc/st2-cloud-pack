from typing import Optional, Dict, List

from openstack.compute.v2.server import Server
from openstack.identity.v3.project import Project
from openstack.exceptions import ResourceNotFound

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.query_runner import QueryRunner

from exceptions.parse_query_error import ParseQueryError
from custom_types.openstack_query.aliases import ProjectIdentifier


class ServerRunner(QueryRunner):
    """
    Runner class for openstack Server resource.
    ServerRunner encapsulates running any openstacksdk Server commands
    """

    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[Dict[str, str]] = None,
        from_projects: Optional[List[ProjectIdentifier]] = None,
    ) -> List[Server]:
        """
        This method runs the query by running openstacksdk commands

        For ServerQuery, this command gets all projects available and iteratively finds servers that belong to that project
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional set of filter kwargs to pass to conn.compute.servers()
            to limit the servers being returned. - see https://docs.openstack.org/api-ref/compute/#list-servers
        :param from_projects: takes a list of openstack projects to run the query on

        """
        projects = self._get_projects(conn, from_projects)
        query_res = self._run_query_on_projects(conn, projects, filter_kwargs).values()
        return [server for project_servers in query_res for server in project_servers]

    def _get_projects(
        self,
        conn: OpenstackConnection,
        projects: Optional[List[ProjectIdentifier]] = None,
    ) -> List[Project]:
        """
        This method gets openstack projects from a list of project identifiers
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param projects: A list of project identifiers to get the associated openstack project object,
        if None, gets all projects
        """
        if not projects:
            return list(conn.identity.projects())

        all_projects = []
        for project in projects:
            if isinstance(project, Project):
                all_projects.append(project)
            else:
                try:
                    all_projects.append(
                        conn.identity.find_project(project, ignore_missing=False)
                    )
                except ResourceNotFound as err:
                    raise ParseQueryError(
                        "Failed to execute query - could not find project to search in"
                    ) from err
        return all_projects

    def _run_query_on_projects(
        self,
        conn: OpenstackConnection,
        projects: List[Project],
        filter_kwargs: Optional[Dict[str, str]] = None,
    ) -> Dict[str, List[Server]]:
        """
        This method is a helper function that will run the query on a list of openstack projects given and return
        a dictionary of servers that match the query grouped by project ids for which the servers belong to
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param projects: A list of openstacksdk projects to run query on
        :param filter_kwargs: An Optional set of filter kwargs to pass to conn.compute.servers()
        """
        return {
            project["id"]: self._run_query_on_project(conn, project, filter_kwargs)
            for project in projects
        }

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
        return list(conn.compute.servers(all_projects=False, **server_filters))

    def _parse_subset(
        self, _: OpenstackConnection, subset: List[Server]
    ) -> List[Server]:
        """
        This method is a helper function that will check a list of servers to ensure that they are valid Server objects
        :param subset: A list of openstack Server objects
        """
        if any(not isinstance(i, Server) for i in subset):
            raise ParseQueryError("'from_subset' only accepts Server openstack objects")
        return subset
