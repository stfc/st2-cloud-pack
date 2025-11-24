from openstackquery.api.query_objects import HypervisorQuery, ServerQuery


def query_hypervisor_state(cloud_account: str):
    """
    Query the state of hypervisors
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
    server_query.group_by("hypervisor_name")
    server_query.run(cloud_account=cloud_account, all_projects=True, as_admin=True)

    servers_on_hypervisor = server_query.to_props()

    for hv in hypervisor_info:
        hv["hypervisor_server_count"] = len(
            servers_on_hypervisor.get(hv["hypervisor_name"], [])
        )

    return hypervisor_info


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

    if not hypervisor_query_down.to_props():
        raise RuntimeError("No hypervisors found in [DOWN] state")

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

    if not hypervisor_query_disabled.to_props():
        raise RuntimeError("No hypervisors found with [DISABLED] status")

    return hypervisor_query_disabled
