from openstackquery.api.query_objects import HypervisorQuery, ServerQuery
from apis.openstack_query_api.server_queries import group_servers_by_hypervisor_name


def query_hypervisor_state(cloud_account: str):
    """
    Query the state of all hypervisors.
    :param cloud_account: A string representing the cloud account to use - set in clouds.yaml
    """
    state_query = HypervisorQuery()
    state_query.where(
        "regex",
        "hypervisor_name",
        value="hv*",
    )
    state_query.select(
        "hypervisor_name",
        "hypervisor_state",
        "hypervisor_status",
        "hypervisor_uptime_days",
        "disabled_reason",
    )
    state_query.run(cloud_account=cloud_account, all_projects=True, as_admin=True)

    hypervisor_info = state_query.to_props()

    server_query = ServerQuery()
    grouped_query = group_servers_by_hypervisor_name(server_query)
    grouped_query.run(cloud_account=cloud_account, all_projects=True, as_admin=True)

    servers_on_hypervisor = grouped_query.to_props()

    for hv in hypervisor_info:
        hv["hypervisor_server_count"] = len(
            servers_on_hypervisor.get(hv["hypervisor_name"], [])
        )

    return hypervisor_info


def find_down_hypervisors(cloud_account: str):
    """
    Use QueryAPI to run the query to find down hypervisors.
    :param cloud_account: A string representing the cloud account to use
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
    Use QueryAPI to run the query to find disabled hypervisors.
    :param cloud_account: A string representing the cloud account to use
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
