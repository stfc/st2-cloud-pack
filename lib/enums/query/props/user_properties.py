from enum import auto
from enums.query.props.prop_enum import PropEnum
from exceptions.parse_query_error import ParseQueryError

# pylint: disable=too-few-public-methods


class UserProperties(PropEnum):
    """
    An enum class for all user properties
    """

    USER_DOMAIN_ID = auto()
    USER_DESCRIPTION = auto()
    USER_EMAIL = auto()
    USER_NAME = auto()
    
    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        try:
            return UserProperties[val.upper()]
        except KeyError as err:
            raise ParseQueryError(
                f"Could not find User Property {val}. "
                f"Available properties are {','.join([prop.name for prop in UserProperties])}"
            ) from err
