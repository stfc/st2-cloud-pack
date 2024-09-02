from enum import Enum, auto
from typing import List

from enums.query.props.hypervisor_properties import HypervisorProperties
from enums.query.query_presets import QueryPresetsGeneric
from openstack_query import HypervisorQuery


class _HypervisorSearchTypes(Enum):
    EMPTY_HVS = auto()


# pylint: disable=too-few-public-methods
class OpenstackHypervisor:
    """
    Class that contains methods for OpenStack hypervisors
    """

    def __init__(self, query_class=HypervisorQuery):
        """
        Initializes the class with an optional hook for DI
        """
        super().__init__()
        self._query_cls = query_class

    def find_hypervisor(self, cloud_account: str, search_type: str):
        """
        Runs a search for hypervisors based on the search type
        """
        try:
            search_type = _HypervisorSearchTypes[search_type]
        except KeyError as exc:
            raise ValueError(f"Invalid search type: {search_type}") from exc

        if search_type == _HypervisorSearchTypes.EMPTY_HVS:
            return self._find_empty_hypervisors(cloud_account)

        raise NotImplementedError(f"Search type {search_type} not implemented")

    def _find_empty_hypervisors(self, cloud_account: str) -> List[str]:
        """
        Finds all hypervisors that have no instances
        cloud_account: str: the cloud account to run the query on
        return: List[str]: a list of sorted hypervisor names
        """
        hv_query = self._query_cls()
        hv_query.where(
            QueryPresetsGeneric.EQUAL_TO,
            HypervisorProperties.HYPERVISOR_VCPUS_USED,
            value=0,
        )
        hv_query.select(HypervisorProperties.HYPERVISOR_NAME)
        results = hv_query.run(cloud_account=cloud_account).to_props(flatten=True)
        return sorted(results["hypervisor_name"])
