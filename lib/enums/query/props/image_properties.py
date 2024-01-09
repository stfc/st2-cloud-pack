from enum import auto
from enums.query.props.prop_enum import PropEnum
from exceptions.query_property_mapping_error import QueryPropertyMappingError


class ImageProperties(PropEnum):
    """
    An enum class for all image properties
    """

    IMAGE_CREATION_DATE = auto()
    IMAGE_CREATION_PROGRESS = auto()
    IMAGE_ID = auto()
    IMAGE_LAST_UPDATED_DATE = auto()
    IMAGE_MINIMUM_DISK = auto()
    IMAGE_MINIMUM_RAM = auto()
    IMAGE_NAME = auto()
    IMAGE_SIZE = auto()
    IMAGE_STATUS = auto()

    @staticmethod
    def _get_aliases():
        """
        A method that returns all valid string alias mappings
        """
        return {
            ImageProperties.IMAGE_CREATION_DATE: ["created_at"],
            ImageProperties.IMAGE_CREATION_PROGRESS: ["progress"],
            ImageProperties.IMAGE_ID: ["id", "uuid"],
            ImageProperties.IMAGE_LAST_UPDATED_DATE: ["updated_at"],
            ImageProperties.IMAGE_MINIMUM_RAM: ["min_ram", "ram"],
            ImageProperties.IMAGE_MINIMUM_DISK: ["min_disk", "disk"],
            ImageProperties.IMAGE_NAME: ["name"],
            ImageProperties.IMAGE_SIZE: ["size"],
            ImageProperties.IMAGE_STATUS: ["status"],
        }

    @staticmethod
    def get_prop_mapping(prop):
        """
        Method that returns the property function if function mapping exists for a given FlavorProperty Enum
        how to get specified property from an openstacksdk Flavor object is documented here:
        https://docs.openstack.org/openstacksdk/latest/user/resources/compute/v2/image.html#openstack.compute.v2.image.Image
        :param prop: A FlavorProperty Enum for which a function may exist for
        """
        mapping = {
            ImageProperties.IMAGE_CREATION_DATE: lambda a: a["created_at"],
            ImageProperties.IMAGE_CREATION_PROGRESS: lambda a: a["progress"],
            ImageProperties.IMAGE_ID: lambda a: a["id"],
            ImageProperties.IMAGE_LAST_UPDATED_DATE: lambda a: a["updated_at"],
            ImageProperties.IMAGE_MINIMUM_DISK: lambda a: a["min_disk"],
            ImageProperties.IMAGE_MINIMUM_RAM: lambda a: a["min_ram"],
            ImageProperties.IMAGE_NAME: lambda a: a["name"],
            ImageProperties.IMAGE_SIZE: lambda a: a["size"],
            ImageProperties.IMAGE_STATUS: lambda a: a["status"],
        }
        try:
            return mapping[prop]
        except KeyError as exp:
            raise QueryPropertyMappingError(
                f"Error: failed to get property mapping, property {prop.name} is not supported in ImageProperties"
            ) from exp

    @staticmethod
    def get_marker_prop_func():
        """
        A getter method to return marker property function for pagination
        """
        return ImageProperties.get_prop_mapping(ImageProperties.IMAGE_ID)
