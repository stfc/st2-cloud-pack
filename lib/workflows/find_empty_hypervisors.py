from enums.query.props.hypervisor_properties import HypervisorProperties
from enums.query.query_presets import QueryPresetsGeneric
from enums.query.sort_order import SortOrder
from openstack_query import HypervisorQuery


def find_empty_hypervisors(cloud_account: str):
    """
    Finds all hypervisors that have no instances
    cloud_account: str: the cloud account to run the query on
    return: List[str]: a list of sorted hypervisor names
    """
    hv_query = HypervisorQuery()
    hv_query.where(
        QueryPresetsGeneric.EQUAL_TO,
        HypervisorProperties.HYPERVISOR_VCPUS_USED,
        value=0,
    )
    hv_query.select(HypervisorProperties.HYPERVISOR_NAME)
    results = (
        hv_query.run(cloud_account=cloud_account)
        .sort_by([HypervisorProperties.HYPERVISOR_NAME, SortOrder.ASC])
        .to_props(flatten=True)
    )
    return results["hypervisor_name"]
