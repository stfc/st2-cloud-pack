from typing import Optional, Dict

from openstack.compute.v2.server import Server
from openstack.identity.v3.project import Project

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.query_wrapper import QueryWrapper
from openstack_query.utils import convert_to_timestamp

from enums.query.server_properties import ServerProperties
from enums.query.query_presets import QueryPresets
from exceptions.parse_query_error import ParseQueryError


class QueryServer(QueryWrapper):
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

    _KWARG_MAPPINGS = {
        QueryPresets.EQUAL_TO: {
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
        QueryPresets.OLDER_THAN_OR_EQUAL_TO: {
            ServerProperties.SERVER_LAST_UPDATED_DATE: lambda **kwargs: {
                "changes-before": convert_to_timestamp(**kwargs)
            }
        },
        QueryPresets.YOUNGER_THAN_OR_EQUAL_TO: {
            ServerProperties.SERVER_LAST_UPDATED_DATE: lambda **kwargs: {
                "changes-since": convert_to_timestamp(**kwargs)
            }
        },
    }

    _DEFAULT_FILTER_FUNCTION_MAPPINGS = {
        QueryPresets.EQUAL_TO: ["*"],
        QueryPresets.NOT_EQUAL_TO: ["*"],
        QueryPresets.OLDER_THAN: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE,
        ],
        QueryPresets.YOUNGER_THAN: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE,
        ],
        QueryPresets.YOUNGER_THAN_OR_EQUAL_TO: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE,
        ],
        QueryPresets.OLDER_THAN_OR_EQUAL_TO: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE,
        ],
        QueryPresets.MATCHES_REGEX: [ServerProperties.SERVER_NAME],
    }

    _NON_DEFAULT_FILTER_FUNCTION_MAPPINGS = {}

    def __init__(self, connection_cls=OpenstackConnection):
        QueryWrapper.__init__(self, connection_cls)

    @staticmethod
    def _run_query(
        conn: OpenstackConnection,
        filter_kwargs: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """
        This method runs the query by running openstacksdk commands
        For QueryServer, this command gets all projects available and iteratively finds servers in that project
        :param conn: An OpenstackConnection object
        :param filter_kwargs: An Optional set of kwargs to pass to conn.compute.servers
        :param kwargs: a set of extra meta params that override openstacksdk commands or change which commands are run

        kwargs: For QueryServer:
            'from_projects' - set which projects to search by providing a list of openstack projects to search in
        """
        servers = []
        if "from_projects" in kwargs:
            projects = kwargs["from_projects"]
        else:
            projects = []
            for project in conn.identity.projects():
                projects.append(project)

        for project in projects:
            servers.extend(
                QueryServer._run_query_on_project(conn, project, filter_kwargs)
            )
        return servers

    @staticmethod
    def _run_query_on_project(
        conn: OpenstackConnection,
        project: Project,
        filter_kwargs: Optional[Dict[str, str]] = None,
    ):
        servers = []

        server_filters = {"project_id": project["id"], "all_tenants": True}

        server_filters.update(filter_kwargs if filter_kwargs else {})
        servers.extend(list(conn.compute.servers(filters=server_filters)))

        return servers

    @staticmethod
    def _parse_subset(conn: OpenstackConnection, server_identifiers: Server):
        query_from = []
        for server_instance in server_identifiers:
            server_obj = server_instance
            if not isinstance(Server, server_instance):
                server_obj = conn.compute.find_server(server_instance)
            query_from.append(server_obj)
        return query_from
