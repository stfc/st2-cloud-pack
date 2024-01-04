from enum import auto
from enums.query.props.prop_enum import PropEnum
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
    FLAVOR_HOSTTYPE = auto()

    @staticmethod
    def _get_aliases():
        """
        A method that returns all valid string alias mappings
        """
        return {
            FlavorProperties.FLAVOR_DESCRIPTION: ["description", "desc"],
            FlavorProperties.FLAVOR_DISK: ["disk", "disk_size"],
            FlavorProperties.FLAVOR_EPHEMERAL: [
                "ephemeral",
                "ephemeral_disk",
                "ephemeral_disk_size",
            ],
            FlavorProperties.FLAVOR_ID: ["id", "uuid"],
            FlavorProperties.FLAVOR_IS_DISABLED: ["is_disabled"],
            FlavorProperties.FLAVOR_IS_PUBLIC: ["is_public"],
            FlavorProperties.FLAVOR_NAME: ["name"],
            FlavorProperties.FLAVOR_RAM: ["ram", "ram_size"],
            FlavorProperties.FLAVOR_SWAP: ["swap", "swap_size"],
            FlavorProperties.FLAVOR_VCPU: ["vcpu", "vcpus", "vcpu_num"],
            FlavorProperties.FLAVOR_HOSTTYPE: ["hosttype"],
        }

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
            FlavorProperties.FLAVOR_HOSTTYPE: lambda a: a["extra_specs"]["aggregate_instance_extra_specs:hosttype"],
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
