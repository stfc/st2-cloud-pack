from typing import Optional, Dict, List

from openstack.compute.v2.server import Server
from openstack.identity.v3.project import Project

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.query_wrapper import QueryWrapper
from openstack_query.utils import convert_to_timestamp

from enums.query.server_properties import ServerProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsInteger,
    QueryPresetsDateTime,
    QueryPresetsString,
)
from exceptions.parse_query_error import ParseQueryError


class QueryServer(QueryWrapper):

    # PROPERTY_MAPPINGS set how to get properties of a openstack server object
    # possible properties are documented here:
    # https://docs.openstack.org/openstacksdk/latest/user/resources/compute/v2/server.html#openstack.compute.v2.server.Server
    _PROPERTY_MAPPINGS = {
        ServerProperties.USER_ID: lambda a: a["user_id"],
        ServerProperties.HYPERVISOR_ID: lambda a: a["host_id"],
        ServerProperties.SERVER_ID: lambda a: a["id"],
        ServerProperties.SERVER_NAME: lambda a: a["name"],
        ServerProperties.SERVER_DESCRIPTION: lambda a: a["description"],
        ServerProperties.SERVER_STATUS: lambda a: a["status"],
        ServerProperties.SERVER_CREATION_DATE: lambda a: a["created_at"],
        ServerProperties.SERVER_LAST_UPDATED_DATE: lambda a: a["updated_at"],
        ServerProperties.FLAVOR_ID: lambda a: ["flavor_id"],
        ServerProperties.IMAGE_ID: lambda a: ["image_id"],
        ServerProperties.PROJECT_ID: lambda a: a["location"]["project"]["id"],
    }

    # KWARG_MAPPINGS - 'filter' keyword arguments that openstack command conn.compute.servers() takes
    # - documented here https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html
    # - all filters are documented here
    # https://docs.openstack.org/api-ref/compute/?expanded=list-servers-detail#list-server-request
    _KWARG_MAPPINGS = {
        QueryPresetsGeneric.EQUAL_TO: {
            ServerProperties.USER_ID: lambda **kwargs: {"user_id": kwargs["value"]},
            ServerProperties.SERVER_ID: lambda **kwargs: {"uuid": kwargs["value"]},
            ServerProperties.SERVER_NAME: lambda **kwargs: {
                "hostname": kwargs["value"]
            },
            ServerProperties.SERVER_DESCRIPTION: lambda **kwargs: {
                "description": kwargs["value"]
            },
            ServerProperties.SERVER_STATUS: lambda **kwargs: {
                "vm_state": kwargs["value"]
            },
            ServerProperties.SERVER_CREATION_DATE: lambda **kwargs: {
                "created_at": kwargs["value"]
            },
            ServerProperties.FLAVOR_ID: lambda **kwargs: {"flavor": kwargs["value"]},
            ServerProperties.IMAGE_ID: lambda **kwargs: {"image": kwargs["value"]},
            ServerProperties.PROJECT_ID: lambda **kwargs: {
                "project_id": kwargs["value"]
            },
        },
        QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: {
            ServerProperties.SERVER_LAST_UPDATED_DATE: lambda **kwargs: {
                "changes-before": convert_to_timestamp(**kwargs)
            }
        },
        QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: {
            ServerProperties.SERVER_LAST_UPDATED_DATE: lambda **kwargs: {
                "changes-since": convert_to_timestamp(**kwargs)
            }
        },
    }

    _DEFAULT_FILTER_FUNCTION_MAPPINGS = {
        QueryPresetsGeneric.EQUAL_TO: ["*"],
        QueryPresetsGeneric.NOT_EQUAL_TO: ["*"],
        QueryPresetsDateTime.OLDER_THAN: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE,
        ],
        QueryPresetsDateTime.YOUNGER_THAN: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE,
        ],
        QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE,
        ],
        QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE,
        ],
        QueryPresetsString.MATCHES_REGEX: [ServerProperties.SERVER_NAME],
    }

    _NON_DEFAULT_FILTER_FUNCTION_MAPPINGS = {}

    def __init__(self, connection_cls=OpenstackConnection):
        QueryWrapper.__init__(self, connection_cls)

    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[Dict[str, str]] = None,
        **kwargs
    ):
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
            if isinstance(kwargs["from_projects"], Project):
                projects = kwargs["from_projects"]
            else:
                raise ParseQueryError(
                    "'from_project' only accepts Openstack 'Project' objects"
                )
        else:
            for project in conn.identity.projects():
                projects.append(project)

        return self._run_query_on_projects(conn, projects, filter_kwargs)

    def _run_query_on_projects(
        self,
        conn: OpenstackConnection,
        projects: List[Project],
        filter_kwargs: Optional[Dict[str, str]] = None,
    ):
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
    ):
        """
        This method is a helper function that will list all servers that belong to a given openstack projects
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param project: An openstacksdk project to run query on
        :param filter_kwargs: An Optional set of filter kwargs to pass to conn.compute.servers()
        """
        server_filters = {"project_id": project["id"], "all_tenants": True}
        server_filters.update(filter_kwargs if filter_kwargs else {})
        return list(conn.compute.servers(filters=server_filters))

    @staticmethod
    def _parse_subset(servers: List[Server]):
        """
        This method is a helper function that will check a list of servers to ensure that they are valid Server objects
        :param servers: A list of openstack Server objects
        """
        for server in servers:
            if not isinstance(server, Server):
                raise ParseQueryError(
                    "'from_subset' only accepts Server openstack objects"
                )
        return servers
