from enum import auto
from enums.query.props.prop_enum import PropEnum
from exceptions.parse_query_error import ParseQueryError
from exceptions.query_property_mapping_error import QueryPropertyMappingError


class ProjectProperties(PropEnum):
    """
    An enum class for all server properties
    """

    PROJECT_DESCRIPTION = auto()
    PROJECT_DOMAIN_ID = auto()
    PROJECT_ID = auto()
    PROJECT_IS_DOMAIN = auto()
    PROJECT_IS_ENABLED = auto()
    PROJECT_NAME = auto()
    PROJECT_PARENT_ID = auto()

    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        try:
            return ProjectProperties[val.upper()]
        except KeyError as err:
            raise ParseQueryError(
                f"Could not find Server Property {val}. "
                f"Available properties are {','.join([prop.name for prop in ProjectProperties])}"
            ) from err

    @staticmethod
    def get_prop_mapping(prop):
        """
        Method that returns the property function if function mapping exists for a given ProjectProperties Enum
        how to get specified property from an openstacksdk Project object is documented here:
        https://docs.openstack.org/openstacksdk/latest/user/resources/identity/v3/project.html#openstack.identity.v3.project.Project
        :param prop: A ProjectProperties Enum for which a function may exist for
        """
        mapping = {
            ProjectProperties.PROJECT_DESCRIPTION: lambda a: a["description"],
            ProjectProperties.PROJECT_DOMAIN_ID: lambda a: a["domain_id"],
            ProjectProperties.PROJECT_ID: lambda a: a["id"],
            ProjectProperties.PROJECT_IS_DOMAIN: lambda a: a["is_domain"],
            ProjectProperties.PROJECT_IS_ENABLED: lambda a: a["is_enabled"],
            ProjectProperties.PROJECT_NAME: lambda a: a["name"],
            ProjectProperties.PROJECT_PARENT_ID: lambda a: a["parent_id"],
        }
        try:
            return mapping[prop]
        except KeyError as exp:
            raise QueryPropertyMappingError(
                "Error: failed to get property mapping, property {prop.name} is not supported in ProjectProperties"
            ) from exp

    @staticmethod
    def get_marker_prop_func():
        """
        A getter method to return marker property function for pagination
        """
        return ProjectProperties.get_prop_mapping(ProjectProperties.PROJECT_ID)
