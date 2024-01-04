from enum import auto
from enums.query.props.prop_enum import PropEnum
from exceptions.query_property_mapping_error import QueryPropertyMappingError


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
    ADDRESSES = auto()

    @staticmethod
    def _get_aliases():
        """
        A method that returns all valid string alias mappings
        """
        return {
            ServerProperties.HYPERVISOR_ID: ["host_id", "hv_id"],
            ServerProperties.SERVER_CREATION_DATE: ["created_at"],
            ServerProperties.SERVER_DESCRIPTION: [
                "description",
                "desc",
                "vm_description",
            ],
            ServerProperties.SERVER_ID: ["vm_id", "id", "uuid"],
            ServerProperties.SERVER_LAST_UPDATED_DATE: ["updated_at"],
            ServerProperties.SERVER_NAME: ["vm_name", "name"],
            ServerProperties.SERVER_STATUS: ["status", "vm_status"],
            ServerProperties.ADDRESSES: ["ips", "vm_ips", "server_ips"],
        }

    @staticmethod
    def get_prop_mapping(prop):
        """
        Method that returns the property function if function mapping exists for a given ServerProperty Enum
        how to get specified property from an openstacksdk Server object is documented here:
        https://docs.openstack.org/openstacksdk/latest/user/resources/compute/v2/server.html#openstack.compute.v2.server.Server
        :param prop: A ServerProperty Enum for which a function may exist for
        """
        mapping = {
            ServerProperties.USER_ID: lambda a: a["user_id"],
            ServerProperties.HYPERVISOR_ID: lambda a: a["host_id"],
            ServerProperties.SERVER_ID: lambda a: a["id"],
            ServerProperties.SERVER_NAME: lambda a: a["name"],
            ServerProperties.SERVER_DESCRIPTION: lambda a: a["description"],
            ServerProperties.SERVER_STATUS: lambda a: a["status"],
            ServerProperties.SERVER_CREATION_DATE: lambda a: a["created_at"],
            ServerProperties.SERVER_LAST_UPDATED_DATE: lambda a: a["updated_at"],
            ServerProperties.FLAVOR_ID: lambda a: a["flavor"]["id"],
            ServerProperties.IMAGE_ID: lambda a: a["image_id"],
            ServerProperties.PROJECT_ID: lambda a: a["location"]["project"]["id"],
            ServerProperties.ADDRESSES: ServerProperties.get_ips,
        }
        try:
            return mapping[prop]
        except KeyError as exp:
            raise QueryPropertyMappingError(
                f"Error: failed to get property mapping, property {prop.name} is not supported in ServerProperties"
            ) from exp

    @staticmethod
    def get_marker_prop_func():
        """
        A getter method to return marker property function for pagination
        """
        return ServerProperties.get_prop_mapping(ServerProperties.SERVER_ID)

    @staticmethod
    def get_ips(obj):
        """
        A method to parse IPs from a server object and output as a comma-spaced string
        :param obj: a openstacksdk server object
        """
        return ", ".join(
            [
                ip.get("addr", [])
                for network in obj["addresses"].values()
                for ip in network
            ]
        )
