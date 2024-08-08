from enum import auto
from typing import Dict, Optional

from enums.query.props.prop_enum import PropEnum, PropFunc
from exceptions.query_property_mapping_error import QueryPropertyMappingError


class HypervisorProperties(PropEnum):
    """
    An enum class for all hypervisor properties
    """

    HYPERVISOR_CURRENT_WORKLOAD = auto()
    HYPERVISOR_DISK_FREE = auto()
    HYPERVISOR_DISK_SIZE = auto()
    HYPERVISOR_DISK_USED = auto()
    HYPERVISOR_ID = auto()
    HYPERVISOR_IP = auto()
    HYPERVISOR_MEMORY_FREE = auto()
    HYPERVISOR_MEMORY_SIZE = auto()
    HYPERVISOR_MEMORY_USED = auto()
    HYPERVISOR_NAME = auto()
    HYPERVISOR_SERVER_COUNT = auto()
    HYPERVISOR_STATE = auto()
    HYPERVISOR_STATUS = auto()
    HYPERVISOR_VCPUS = auto()
    HYPERVISOR_VCPUS_USED = auto()
    HYPERVISOR_DISABLED_REASON = auto()

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
            HypervisorProperties.HYPERVISOR_DISK_FREE: [
                "local_disk_free",
                "free_disk_gb",
            ],
            HypervisorProperties.HYPERVISOR_DISK_SIZE: ["local_disk_size", "local_gb"],
            HypervisorProperties.HYPERVISOR_DISK_USED: [
                "local_disk_used",
                "local_gb_used",
            ],
            HypervisorProperties.HYPERVISOR_ID: ["id", "uuid", "host_id"],
            HypervisorProperties.HYPERVISOR_IP: ["ip", "host_ip"],
            HypervisorProperties.HYPERVISOR_MEMORY_FREE: ["memory_free", "free_ram_mb"],
            HypervisorProperties.HYPERVISOR_MEMORY_SIZE: ["memory_size", "memory_mb"],
            HypervisorProperties.HYPERVISOR_MEMORY_USED: [
                "memory_used",
                "memory_mb_used",
            ],
            HypervisorProperties.HYPERVISOR_NAME: ["name", "host_name"],
            HypervisorProperties.HYPERVISOR_SERVER_COUNT: ["running_vms"],
            HypervisorProperties.HYPERVISOR_STATE: ["state"],
            HypervisorProperties.HYPERVISOR_STATUS: ["status"],
            HypervisorProperties.HYPERVISOR_VCPUS: ["vcpus"],
            HypervisorProperties.HYPERVISOR_VCPUS_USED: ["vcpus_used"],
            HypervisorProperties.HYPERVISOR_DISABLED_REASON: ["disabled_reason"],
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
            HypervisorProperties.HYPERVISOR_DISK_FREE: lambda a: a["free_disk_gb"],
            HypervisorProperties.HYPERVISOR_DISK_SIZE: lambda a: a["local_gb"],
            HypervisorProperties.HYPERVISOR_DISK_USED: lambda a: a["local_gb_used"],
            HypervisorProperties.HYPERVISOR_ID: lambda a: a["id"],
            HypervisorProperties.HYPERVISOR_IP: lambda a: a["host_ip"],
            HypervisorProperties.HYPERVISOR_MEMORY_FREE: lambda a: a["free_ram_mb"],
            HypervisorProperties.HYPERVISOR_MEMORY_SIZE: lambda a: a["memory_mb"],
            HypervisorProperties.HYPERVISOR_MEMORY_USED: lambda a: a["memory_mb_used"],
            HypervisorProperties.HYPERVISOR_NAME: lambda a: a["name"],
            HypervisorProperties.HYPERVISOR_SERVER_COUNT: lambda a: a["runnning_vms"],
            HypervisorProperties.HYPERVISOR_STATE: lambda a: a["state"],
            HypervisorProperties.HYPERVISOR_STATUS: lambda a: a["status"],
            HypervisorProperties.HYPERVISOR_VCPUS: lambda a: a["vcpus"],
            HypervisorProperties.HYPERVISOR_VCPUS_USED: lambda a: a["vcpus_used"],
            HypervisorProperties.HYPERVISOR_DISABLED_REASON: lambda a: a["service"][
                "disabled_reason"
            ],
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
