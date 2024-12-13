from openstackquery.api.query_objects import HypervisorQuery, ServerQuery


def query_hypervisor_state(cloud_account: str):
    """
    Query the state of hypervisors
    :param cloud_account: A string representing the cloud account to use - set in clouds.ymal
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
    )

    state_query.run(cloud_account=cloud_account, all_projects=True, as_admin=True)
    hypervisor_info = state_query.to_props()
    server_query = ServerQuery()
    server_query.group_by("hypervisor_name")
    server_query.run(cloud_account=cloud_account, all_projects=True, as_admin=True)

    servers_on_hypervisor = server_query.to_props()

    for hv in hypervisor_info:
        hv["hypervisor_server_count"] = len(
            servers_on_hypervisor.get(hv["hypervisor_name"], [])
        )

    return hypervisor_info
