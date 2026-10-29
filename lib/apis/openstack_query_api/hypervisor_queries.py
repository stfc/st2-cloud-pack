from typing import Dict, List

from openstackquery.api.query_objects import HypervisorQuery, ServerQuery

from apis.openstack_query_api import QueryThread
from workflows.query_netbox_for_hypervisor_firmware_date import (
    query_netbox_for_hypervisor_firmware_date,
)


def query_hypervisor_state(cloud_account: str) -> List[Dict]:
    """
    Query the state of hypervisors from Openstack and Netbox
    :param cloud_account: A string representing the cloud account to use - set in clouds.yaml
    """

    def get_hypervisors():
        # Temp whitelist for prod to limit hypervisors auto drained
        if cloud_account.casefold() == "prod":
            hv_regex = "^hv[8].*"
        else:
            hv_regex = "^hv"

        state_query = HypervisorQuery()
        state_query.where(
            "regex",
            "hypervisor_name",
            value=hv_regex,
        )
        state_query.where(
            "not_equal_to",
            "hypervisor_uptime_days",
            value=None,
        )
        state_query.select(
            "hypervisor_name",
            "hypervisor_state",
            "hypervisor_status",
            "hypervisor_uptime_days",
            "disabled_reason",
        )
        state_query.run(cloud_account=cloud_account, all_projects=True, as_admin=True)
        return state_query.to_props()

    def get_servers():
        server_query = ServerQuery()
        server_query.group_by("hypervisor_name")
        server_query.run(cloud_account=cloud_account, all_projects=True, as_admin=True)
        return server_query.to_props()

    threads = []
    hypervisors_thread = QueryThread(target=get_hypervisors)
    netbox_thread = QueryThread(
        target=query_netbox_for_hypervisor_firmware_date,
        args=(cloud_account, "prod" if cloud_account == "prod" else "staging", "any"),
    )
    servers_thread = QueryThread(target=get_servers)

    threads.append(hypervisors_thread)
    threads.append(netbox_thread)
    threads.append(servers_thread)

    for thread in threads:
        thread.start()

    hypervisors: List[Dict] = hypervisors_thread.join() or []
    netbox_info: List[Dict] = netbox_thread.join() or []
    servers: List[Dict] = servers_thread.join() or []

    merged_hypervisors = []
    for hv in hypervisors:
        hv["hypervisor_server_count"] = len(servers.get(hv["hypervisor_name"], []))

        netbox_data = next(x for x in netbox_info if x["name"] == hv["hypervisor_name"])
        hv = {**hv, **netbox_data}
        merged_hypervisors.append(hv)

    return merged_hypervisors


def find_down_hypervisors(cloud_account: str):
    """
    :param cloud_account: string represents cloud account to use
    """

    hypervisor_query_down = HypervisorQuery()
    hypervisor_query_down.where(
        "any_in",
        "hypervisor_state",
        values=["down"],
    )
    hypervisor_query_down.run(
        cloud_account,
    )
    hypervisor_query_down.select(
        "hypervisor_id",
        "hypervisor_name",
        "hypervisor_state",
        "hypervisor_status",
    )

    return hypervisor_query_down


def find_disabled_hypervisors(cloud_account: str):
    """
    :param cloud_account: string represents cloud account to use
    """

    hypervisor_query_disabled = HypervisorQuery()
    hypervisor_query_disabled.where(
        "any_in",
        "hypervisor_status",
        values=["disabled"],
    )
    hypervisor_query_disabled.run(
        cloud_account,
    )
    hypervisor_query_disabled.select(
        "hypervisor_id",
        "hypervisor_name",
        "hypervisor_state",
        "hypervisor_status",
    )

    return hypervisor_query_disabled
