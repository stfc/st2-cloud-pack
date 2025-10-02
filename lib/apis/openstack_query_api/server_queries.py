from typing import List, Optional
from openstackquery import FlavorQuery

def find_servers_with_flavors(
    cloud_account: str,
    flavor_name_list: List[str],
    from_projects: Optional[List[str]] = None,
):
    """
    Use QueryAPI to run the query to find decom flavors
    :param cloud_account: string represents cloud account to use
    :param flavor_name_list: A list of flavor names to be decommissioned
    :param from_projects: A list of project identifiers to limit search in
    """

    flavor_query = FlavorQuery()
    flavor_query.where(
        "any_in",
        "flavor_name",
        values=flavor_name_list,
    )
    flavor_query.run(cloud_account)
    flavor_query.sort_by(("flavor_id", "asc"))

    if not flavor_query.to_props():
        raise RuntimeError(
            f"None of the Flavors provided {', '.join(flavor_name_list)} were found"
        )

    # find the VMs using flavors we found from the flavor query
    server_query = flavor_query.then("SERVER_QUERY", keep_previous_results=True)
    server_query.run(
        cloud_account,
        as_admin=True,
        from_projects=from_projects if from_projects else None,
        all_projects=not from_projects,
    )
    server_query.select(
        "server_id",
        "server_name",
        "addresses",
    )

    if not server_query.to_props():
        raise RuntimeError(
            f"No servers found with flavors {', '.join(flavor_name_list)} on projects "
            f"{','.join(from_projects) if from_projects else '[all projects]'}"
        )

    server_query.append_from("PROJECT_QUERY", cloud_account, ["project_name"])
    server_query.group_by("user_id")

    return server_query
