import re
from typing import List, Optional

from openstackquery import HypervisorQuery

# pylint:disable=too-many-arguments


def find_reinstall_candidate_hypervisors(
    cloud_account: str,
    max_vcpus: Optional[int] = 60,
    exclude_hostnames: Optional[List[str]] = None,
    properties_to_select: Optional[List[str]] = None,
    output_type: Optional[str] = "to_string",
    sort_direction: Optional[str] = "desc",
    **kwargs,
):
    """
    Method that builds and runs a query to find generic numerical resource based on a expression
    (less-than, greater-than etc)
    :param cloud_account: A string representing the cloud account to use - set in clouds.yaml
    :param max_vcpus: int of the maximum allowed number of VCPUs used
    :param properties_to_select: list of strings representing which properties to select
    :param output_type: string representing how to output the query
    :param sort_direction: string representing which direction to sort the results by vcpus_used, asc or desc
    :param kwargs: A set of optional meta params to pass to the query
    """

    query = HypervisorQuery()
    if not properties_to_select:
        query.select_all()
    else:
        query.select(*properties_to_select)

    query.where(
        preset="MATCHES_REGEX",
        prop="ip",
        value=r"^172\.16\.(?:\d{1,3})\.(?:\d{1,3})$",
    )

    query.where(preset="LESS_THAN_OR_EQUAL_TO", prop="vcpus_used", value=max_vcpus)

    # TODO: Add option to allow for disabled servers where the reason matches a set of allowed reasons
    query.where(preset="EQUAL_TO", prop="state", value="up")

    query.where(preset="EQUAL_TO", prop="status", value="enabled")

    # TODO: Add custom openstackquery query for NOT_MATCHES_REGEX, lookahead filters like this aren't performant
    if exclude_hostnames:
        escaped_hostnames = [re.escape(h) for h in exclude_hostnames]
        hostname_pattern = f"^(?!.*({'|'.join(escaped_hostnames)})).*$"

        query.where(
            preset="MATCHES_REGEX",
            prop="name",
            value=hostname_pattern,
        )

    query.sort_by(("vcpus_used", sort_direction))

    query.run(cloud_account, **kwargs)

    return {
        "to_html": query.to_html(),
        "to_string": query.to_string(),
        "to_objects": query.to_objects(),
        "to_props": query.to_props(),
    }[output_type]
