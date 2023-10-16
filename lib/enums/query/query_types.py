from enum import Enum
from exceptions.parse_query_error import ParseQueryError

from openstack_query.mappings.flavor_mapping import FlavorMapping
from openstack_query.mappings.project_mapping import ProjectMapping
from openstack_query.mappings.server_mapping import ServerMapping
from openstack_query.mappings.user_mapping import UserMapping


class QueryTypes(Enum):
    """
    Enum class which holds enums for different query objects. Used when
    specifying queries to chain to
    """

    FLAVOR_QUERY = FlavorMapping
    PROJECT_QUERY = ProjectMapping
    SERVER_QUERY = ServerMapping
    USER_QUERY = UserMapping

    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        try:
            return QueryTypes[val.upper()]
        except KeyError as err:
            raise ParseQueryError(
                f"Could not find query type {val}. "
                f"Available query types are {','.join([prop.name for prop in QueryTypes])}"
            ) from err
