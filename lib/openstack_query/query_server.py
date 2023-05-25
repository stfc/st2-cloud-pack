from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.query_wrapper import QueryWrapper

from enums.query.server_properties import ServerProperties
from enums.query.query_presets import QueryPresets


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
        ServerProperties.FLAVOR_ID: lambda a: ['flavor_id'],
        ServerProperties.IMAGE_ID: lambda a: ['image_id'],
        ServerProperties.PROJECT_ID: lambda a: a["location"]["project"]["id"],
    }
    
    _DEFAULT_FILTER_FUNCTION_MAPPINGS = {
        QueryPresets.EQUAL_TO: ['*'],
        QueryPresets.NOT_EQUAL_TO: ['*'],
        QueryPresets.OLDER_THAN: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE
        ],
        QueryPresets.YOUNGER_THAN: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE
        ],
        QueryPresets.YOUNGER_THAN_OR_EQUAL_TO: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE
        ],
        QueryPresets.OLDER_THAN_OR_EQUAL_TO: [
            ServerProperties.SERVER_CREATION_DATE,
            ServerProperties.SERVER_LAST_UPDATED_DATE
        ],
        QueryPresets.MATCHES_REGEX: [
            ServerProperties.SERVER_NAME
        ]
    }

    _NON_DEFAULT_FILTER_FUNCTION_MAPPINGS = {}


    def __init__(self, connection_cls=OpenstackConnection):
        QueryWrapper.__init__(self, connection_cls)

    @staticmethod
    def _run_query(conn: OpenstackConnection, **kwargs):
        """
        This method runs the query by running openstacksdk commands
        For QueryServer, this command gets all projects available and iteratively finds servers in that project
        :param conn: An OpenstackConnection object
        :param kwargs: a set of extra params to pass into conn.compute.servers
        """
        servers = []
        for project in conn.identity.projects():
            server_filters = {
                "project_id": project['id'],
                "all_tenants": True
            }
            server_filters.update(kwargs)
            servers.extend(list(conn.compute.servers(filters=server_filters)))

        return servers



