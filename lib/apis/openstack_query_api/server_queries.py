from typing import List, Optional
from openstackquery import FlavorQuery


def find_server_with_flavors(
    cloud_account: str,
    flavor_name_list: List[str],
    from_projects: Optional[List[str]] = None,
):
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
    # Removed: raise RuntimeError if server_query.to_props() is empty (as per instruction 1.2)
    server_query.append_from("PROJECT_QUERY", cloud_account, ["project_name"])
    # Removed: server_query.group_by("user_id") (as per instruction 1.3)
    return server_query


def group_by(server_query, label):
    return server_query.group_by(label)
