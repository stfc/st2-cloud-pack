from typing import Dict

from enums.query.enum_with_aliases import EnumWithAliases

from openstack_query.mappings.flavor_mapping import FlavorMapping
from openstack_query.mappings.project_mapping import ProjectMapping
from openstack_query.mappings.server_mapping import ServerMapping
from openstack_query.mappings.user_mapping import UserMapping


class QueryTypes(EnumWithAliases):
    """
    Enum class which holds enums for different query objects. Used when
    specifying queries to chain to
    """

    FLAVOR_QUERY = FlavorMapping
    PROJECT_QUERY = ProjectMapping
    SERVER_QUERY = ServerMapping
    USER_QUERY = UserMapping

    @staticmethod
    def _get_aliases() -> Dict:
        return {
            QueryTypes.FLAVOR_QUERY: [
                "flavor",
                "flavors",
                "query_flavors",
                "to_flavor_query",
            ],
            QueryTypes.PROJECT_QUERY: [
                "project",
                "projects",
                "query_projects",
                "to_project_query",
            ],
            QueryTypes.SERVER_QUERY: [
                "server",
                "servers",
                "query_servers",
                "to_server_query",
            ],
            QueryTypes.USER_QUERY: ["user", "users", "query_users", "to_user_query"],
        }
