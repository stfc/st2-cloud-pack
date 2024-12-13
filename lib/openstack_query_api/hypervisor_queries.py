from openstackquery.api.query_objects import HypervisorQuery


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
        "hypervisor_server_count",
    )

    state_query.run(cloud_account=cloud_account)

    return state_query.to_props()
