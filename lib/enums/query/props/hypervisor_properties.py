from enum import auto
from typing import Dict, Optional

from enums.query.props.prop_enum import PropEnum, PropFunc
from exceptions.query_property_mapping_error import QueryPropertyMappingError


class HypervisorProperties(PropEnum):
    """
    An enum class for all hypervisor properties
    """

    HYPERVISOR_CURRENT_WORKLOAD = auto()
    HYPERVISOR_DISK_AVAILABLE = auto()
    HYPERVISOR_LOCAL_DISK_FREE = auto()
    HYPERVISOR_LOCAL_DISK_SIZE = auto()
    HYPERVISOR_LOCAL_DISK_USED = auto()
    HYPERVISOR_ID = auto()
    HYPERVISOR_IP = auto()
    HYPERVISOR_MEMORY_FREE = auto()
    HYPERVISOR_MEMORY_SIZE = auto()
    HYPERVISOR_MEMORY_USED = auto()
    HYPERVISOR_NAME = auto()
    HYPERVISOR_SERVER_COUNT = auto()
    HYPERVISOR_SERVER_LIST = auto()
    HYPERVISOR_STATE = auto()
    HYPERVISOR_STATUS = auto()
    HYPERVISOR_UPTIME = auto()
    HYPERVISOR_VCPUS = auto()
    HYPERVISOR_VCPUS_USED = auto()

    @staticmethod
    def _get_aliases() -> Dict:
        """
        A method that returns all valid string alias mappings
        """
        return {
            HypervisorProperties.HYPERVISOR_CURRENT_WORKLOAD: [
                "current_workload",
                "workload",
            ],
            HypervisorProperties.HYPERVISOR_DISK_AVAILABLE: ["disk_available"],
            HypervisorProperties.HYPERVISOR_LOCAL_DISK_FREE: ["local_disk_free"],
            HypervisorProperties.HYPERVISOR_LOCAL_DISK_SIZE: ["local_disk_size"],
            HypervisorProperties.HYPERVISOR_LOCAL_DISK_USED: ["local_disk_used"],
            HypervisorProperties.HYPERVISOR_ID: ["id", "uuid", "host_id"],
            HypervisorProperties.HYPERVISOR_IP: ["ip", "host_ip"],
            HypervisorProperties.HYPERVISOR_MEMORY_FREE: ["memory_free"],
            HypervisorProperties.HYPERVISOR_MEMORY_SIZE: ["memory_size"],
            HypervisorProperties.HYPERVISOR_MEMORY_USED: ["memory_free"],
            HypervisorProperties.HYPERVISOR_NAME: ["name", "host_name"],
            HypervisorProperties.HYPERVISOR_SERVER_COUNT: ["runnning_vms"],
            HypervisorProperties.HYPERVISOR_SERVER_LIST: ["servers", "vms"],
            HypervisorProperties.HYPERVISOR_STATE: ["state"],
            HypervisorProperties.HYPERVISOR_STATUS: ["status"],
            HypervisorProperties.HYPERVISOR_UPTIME: ["uptime"],
            HypervisorProperties.HYPERVISOR_VCPUS: ["vcpus"],
            HypervisorProperties.HYPERVISOR_VCPUS_USED: ["vcpus_used"],
        }

    @staticmethod
    def get_prop_mapping(prop) -> Optional[PropFunc]:
        """
        Method that returns the property function if function mapping exists for a given Hypervisor Enum
        how to get specified property from an openstacksdk Hypervisor object is documented here:
        https://docs.openstack.org/openstacksdk/latest/user/resources/compute/v2/hypervisor.html
        :param prop: A HypervisorProperty Enum for which a function may exist for
        """
        mapping = {
            HypervisorProperties.HYPERVISOR_CURRENT_WORKLOAD: lambda a: a[
                "current_workload"
            ],
            HypervisorProperties.HYPERVISOR_DISK_AVAILABLE: lambda a: a[
                "disk_available"
            ],
            HypervisorProperties.HYPERVISOR_LOCAL_DISK_FREE: lambda a: a[
                "local_disk_free"
            ],
            HypervisorProperties.HYPERVISOR_LOCAL_DISK_SIZE: lambda a: a[
                "local_disk_size"
            ],
            HypervisorProperties.HYPERVISOR_LOCAL_DISK_USED: lambda a: a[
                "local_disk_used"
            ],
            HypervisorProperties.HYPERVISOR_ID: lambda a: a["id"],
            HypervisorProperties.HYPERVISOR_IP: lambda a: a["host_ip"],
            HypervisorProperties.HYPERVISOR_MEMORY_FREE: lambda a: a["memory_free"],
            HypervisorProperties.HYPERVISOR_MEMORY_SIZE: lambda a: a["memory_size"],
            HypervisorProperties.HYPERVISOR_MEMORY_USED: lambda a: a["memory_free"],
            HypervisorProperties.HYPERVISOR_NAME: lambda a: a["name"],
            HypervisorProperties.HYPERVISOR_SERVER_COUNT: lambda a: a["runnning_vms"],
            HypervisorProperties.HYPERVISOR_SERVER_LIST: lambda a: a["servers"],
            HypervisorProperties.HYPERVISOR_STATE: lambda a: a["state"],
            HypervisorProperties.HYPERVISOR_STATUS: lambda a: a["status"],
            HypervisorProperties.HYPERVISOR_UPTIME: lambda a: a["uptime"],
            HypervisorProperties.HYPERVISOR_VCPUS: lambda a: a["vcpus"],
            HypervisorProperties.HYPERVISOR_VCPUS_USED: lambda a: a["vcpus_used"],
        }
        try:
            return mapping[prop]
        except KeyError as exp:
            raise QueryPropertyMappingError(
                f"Error: failed to get property mapping, property {prop.name} is not supported in HypervisorProperties"
            ) from exp

    @staticmethod
    def get_marker_prop_func():
        """
        A getter method to return marker property function for pagination
        """
        return HypervisorProperties.get_prop_mapping(HypervisorProperties.HYPERVISOR_ID)
