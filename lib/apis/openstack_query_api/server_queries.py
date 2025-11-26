from typing import List, Optional
from openstackquery import ImageQuery, ServerQuery, FlavorQuery
from openstackquery.api.query_api import QueryAPI
from apis.utils.regex_utils import list_to_regex_pattern

from workflows.to_webhook import to_webhook


def find_servers_on_hv(
    cloud_account: str,
    hypervisor_name: str,
    from_projects: Optional[List[str]] = None,
    webhook: Optional[str] = None,
):
    """
    :param cloud_account: string represents cloud account to use
    :param from_projects: A list of project identifiers to limit search in
    """

    # Find VMs that have been on a hypervisor
    server_query = ServerQuery()
    server_query.where(
        "equal_to",
        "hypervisor_name",
        value=hypervisor_name,
    )
    server_query.run(
        cloud_account,
        as_admin=True,
        from_projects=from_projects if from_projects else None,
        all_projects=not from_projects,
    )

    server_query.select("id", "name", "addresses")

    if webhook:
        to_webhook(webhook=webhook, payload=server_query.select_all().to_props())

    server_query.append_from("PROJECT_QUERY", cloud_account, ["name"])

    return server_query


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

    server_query.append_from("PROJECT_QUERY", cloud_account, ["project_name"])

    return server_query


def find_servers_with_errored_vms(
    cloud_account: str,
    age_filter_value: int,
    from_projects: Optional[List[str]] = None,
) -> ServerQuery:
    """
    Search for machines that are in error state and returns the user id, name and email address.
    :param cloud_account: String representing cloud account to use
    :param age_filter_value: An integer which specifies the minimum age (in days) of the servers to be found
    :param from_projects: A list of project identifiers to limit search to
    """
    server_query = ServerQuery()
    if age_filter_value > 0:
        server_query.where(
            "older_than",
            "server_last_updated_date",
            days=age_filter_value,
        )
    server_query.where("any_in", "server_status", values=["ERROR"])
    server_query.run(
        cloud_account,
        as_admin=True,
        from_projects=from_projects if from_projects else None,
        all_projects=not from_projects,
    )

    server_query.select("id", "name", "addresses")

    server_query.append_from("PROJECT_QUERY", cloud_account, ["name"])

    return server_query


def find_shutoff_servers(cloud_account: str, from_projects: Optional[List[str]] = None):
    """
    :param cloud_account: string represents cloud account to use
    :param from_projects: A list of project identifiers to limit search in
    """

    # Find VMs that have been in shutoff state for more than 60 days
    server_query = ServerQuery()
    server_query.where("any_in", "server_status", values=["SHUTOFF"])
    server_query.run(
        cloud_account,
        as_admin=True,
        from_projects=from_projects if from_projects else None,
        all_projects=not from_projects,
    )

    server_query.select("id", "name", "addresses")

    server_query.append_from("PROJECT_QUERY", cloud_account, ["name"])

    return server_query


def find_servers_with_image(
    cloud_account: str,
    image_name_list: List[str],
    from_projects: Optional[List[str]] = None,
):
    """
    Use QueryAPI to run the query to find images
    :param cloud_account: String representing the cloud account to use
    :param image_name_list: A list of image names
    :param from_projects: A list of project identifiers to limit the search to
    """
    image_query = ImageQuery()
    image_query.where(
        "matches_regex",
        "name",
        value=list_to_regex_pattern(image_name_list),
    )
    image_query.run(
        cloud_account,
        as_admin=True,
        from_projects=from_projects if from_projects else None,
        all_projects=not from_projects,
    )
    image_query.sort_by(("id", "ascending"), ("name", "ascending"))
    image_query.select("name")

    if not image_query.to_props():
        raise RuntimeError(
            f"None of the Images provided {', '.join(image_name_list)} were found"
        )

    # find the VMs using images we found from the image query
    server_query = image_query.then("SERVER_QUERY", keep_previous_results=True)
    server_query.run(
        cloud_account,
        as_admin=True,
        from_projects=from_projects or None,
        all_projects=not from_projects,
    )
    server_query.select(
        "id",
        "name",
        "addresses",
    )

    server_query.append_from("PROJECT_QUERY", cloud_account, ["name"])

    return server_query


def group_servers_by_user_id(server_query: QueryAPI):
    """
    Group the servers in a server query by "user_id" and return the results
    :param server_query: QueryAPI object containing the results of a server query
    """
    grouped_query = server_query.group_by("user_id")

    return grouped_query
