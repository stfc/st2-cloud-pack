from enum import auto
from enums.query.props.prop_enum import PropEnum
from exceptions.parse_query_error import ParseQueryError
from exceptions.query_property_mapping_error import QueryPropertyMappingError


class FlavorProperties(PropEnum):
    """
    An enum class for all flavor properties
    """

    FLAVOR_DESCRIPTION = auto()
    FLAVOR_DISK = auto()
    FLAVOR_EPHEMERAL = auto()
    FLAVOR_ID = auto()
    FLAVOR_IS_DISABLED = auto()
    FLAVOR_IS_PUBLIC = auto()
    FLAVOR_NAME = auto()
    FLAVOR_RAM = auto()
    FLAVOR_SWAP = auto()
    FLAVOR_VCPU = auto()

    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        try:
            return FlavorProperties[val.upper()]
        except KeyError as err:
            raise ParseQueryError(
                f"Could not find Flavor Property {val}. "
                f"Available properties are {','.join([prop.name for prop in FlavorProperties])}"
            ) from err

    @staticmethod
    def get_prop_mapping(prop):
        """
        Method that returns the property function if function mapping exists for a given FlavorProperty Enum
        how to get specified property from an openstacksdk Flavor object is documented here:
        https://docs.openstack.org/openstacksdk/latest/user/resources/compute/v2/flavor.html#openstack.compute.v2.flavor.Flavor
        :param prop: A FlavorProperty Enum for which a function may exist for
        """
        mapping = {
            FlavorProperties.FLAVOR_DESCRIPTION: lambda a: a["description"],
            FlavorProperties.FLAVOR_DISK: lambda a: a["disk"],
            FlavorProperties.FLAVOR_EPHEMERAL: lambda a: a["ephemeral"],
            FlavorProperties.FLAVOR_ID: lambda a: a["id"],
            FlavorProperties.FLAVOR_IS_DISABLED: lambda a: a["is_disabled"],
            FlavorProperties.FLAVOR_IS_PUBLIC: lambda a: a["is_public"],
            FlavorProperties.FLAVOR_NAME: lambda a: a["name"],
            FlavorProperties.FLAVOR_RAM: lambda a: a["ram"],
            FlavorProperties.FLAVOR_SWAP: lambda a: a["swap"],
            FlavorProperties.FLAVOR_VCPU: lambda a: a["vcpus"],
        }
        try:
            return mapping[prop]
        except KeyError as exp:
            raise QueryPropertyMappingError(
                f"Error: failed to get property mapping, property {prop.name} is not supported in FlavorProperties"
            ) from exp

    @staticmethod
    def get_marker_prop_func():
        """
        A getter method to return marker property function for pagination
        """
        return FlavorProperties.get_prop_mapping(FlavorProperties.FLAVOR_ID)
