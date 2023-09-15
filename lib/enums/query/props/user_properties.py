from enum import auto
from enums.query.props.prop_enum import PropEnum
from exceptions.query_property_mapping_error import QueryPropertyMappingError


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
        return UserProperties._from_string_impl(val, UserProperties)

    @staticmethod
    def get_prop_mapping(prop):
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
        for i in UserProperties:
            assert (
                i in mapping
            ), f"Error: No prop mapping defined for prop UserProperties.{i.name}"

        if prop not in UserProperties:
            raise QueryPropertyMappingError(
                "Error: failed to get property mapping, property is not supported in UserProperties"
            )
        return mapping[prop]

    @staticmethod
    def get_marker_prop_func():
        """
        A getter method to return marker property function for pagination
        """
        return UserProperties.get_prop_mapping(UserProperties.USER_ID)
