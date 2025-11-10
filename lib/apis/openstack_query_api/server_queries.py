import re

from typing import List, Optional
from openstackquery import ImageQuery
from openstackquery.api.query_api import QueryAPI


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


def list_to_regex_pattern(string_list):
    """
    converts a list of strings into a regex pattern that matches any occurrence of any string in the input list.
    :param string_list: a list of strings
    """
    escaped_strings = [re.escape(s) for s in string_list]
    regex_pattern = "|.*".join(escaped_strings)
    return f"(.*{regex_pattern})"
