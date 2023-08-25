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
    USER_ID = auto()
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

    @staticmethod
    def get_prop_func(prop):
        """
        Method that returns the property function if function mapping exists for a given UserProperty Enum
        how to get specified property from an openstacksdk Server object is documented here:
        https://docs.openstack.org/openstacksdk/latest/user/resources/identity/v3/user.html#openstack.identity.v3.user.User
        :param prop: A UserProperty Enum for which a function may exist for
        """
        mapping = {
            UserProperties.USER_ID: lambda a: a["id"],
            UserProperties.USER_DOMAIN_ID: lambda a: a["domain_id"],
            UserProperties.USER_DESCRIPTION: lambda a: a["description"],
            UserProperties.USER_EMAIL: lambda a: a["email"],
            UserProperties.USER_NAME: lambda a: a["name"],
        }
        assert all(i in mapping for i in UserProperties)
        return mapping[prop]

    @staticmethod
    def get_marker_prop_func():
        """
        A getter method to return marker property function for pagination
        """
        return UserProperties.get_prop_func(UserProperties.SERVER_ID)
