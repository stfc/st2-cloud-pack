from enum import auto
from enums.query.props.prop_enum import PropEnum
from exceptions.parse_query_error import ParseQueryError

# pylint: disable=too-few-public-methods


class ServerProperties(PropEnum):
    """
    An enum class for all server properties
    """

    FLAVOR_ID = auto()
    HYPERVISOR_ID = auto()
    IMAGE_ID = auto()
    PROJECT_ID = auto()
    SERVER_CREATION_DATE = auto()
    SERVER_DESCRIPTION = auto()
    SERVER_ID = auto()
    SERVER_LAST_UPDATED_DATE = auto()
    SERVER_NAME = auto()
    SERVER_STATUS = auto()
    USER_ID = auto()

    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        try:
            return ServerProperties[val.upper()]
        except KeyError as err:
            raise ParseQueryError(
                f"Could not find Server Property {val}. "
                f"Available properties are {','.join([prop.name for prop in ServerProperties])}"
            ) from err
