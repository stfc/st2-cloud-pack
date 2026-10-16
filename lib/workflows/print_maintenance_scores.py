import tabulate

from apis.openstack_api.openstack_hypervisor import Hypervisor, prioritse_patching
from apis.openstack_query_api.hypervisor_queries import query_hypervisor_state


def print_maintenance_scores(cloud_account: str) -> None:
    """
    Action for testing the ordering hypervisors by need of maintenance

    :param cloud_account: A string representing the cloud account to use - set in clouds.yaml
    :type cloud_account: str
    """
    data = query_hypervisor_state(cloud_account)

    hypervisor_list = [Hypervisor.from_dict(cloud_account, hv) for hv in data]
    sorted_hypervisors = prioritse_patching(hypervisor_list)

    table_data = [hv.to_dict() for hv in sorted_hypervisors]
    table = tabulate.tabulate(table_data, headers="keys")
    print(table)
