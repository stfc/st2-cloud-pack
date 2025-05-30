import re
from typing import List, Optional

from openstackquery import HypervisorQuery

# pylint:disable=too-many-arguments


def find_reinstall_candidate_hypervisors(
    cloud_account: str,
    ip_regex: Optional[str] = r"^172\.16\.(?:\d{1,3})\.(?:\d{1,3})$",
    max_vcpus: Optional[int] = None,
    max_vms: Optional[int] = None,
    exclude_hostnames: Optional[List[str]] = None,
    properties_to_select: Optional[List[str]] = None,
    output_type: Optional[str] = "to_string",
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = "desc",
    **kwargs,
):
    """
    Finds candidate hypervisors for reinstallation based on resource usage,
    hostname/IP filtering, and allowed or disallowed flavor types.

    :param cloud_account: A string representing the cloud account to use - set in clouds.yaml
    :param ip_regex: Regular expression pattern to filter hypervisor IPs (default: "172.16.x.x").
    :param max_vcpus: Optional maximum threshold for used vCPUs.
    :param max_vms: Optional maximum threshold for # of hosted VMs.
    :param exclude_hostnames: Optional list of hypervisor hostname substrings to exclude.
    :param properties_to_select: Optional list of strings representing which properties to select,
    else all are selected.
    :param output_type: Format of the output (e.g., "to_string", "to_html", "to_props", to_objects").
    :param sort_by: Optional property to sort the results by.
    :param sort_direction: Sort direction for the results; either "asc" or "desc" (default: "desc").
    :param kwargs: A set of optional meta params to pass to the query

    :return: Query result in the specified output format.
    """

    query = HypervisorQuery()
    if not properties_to_select:
        query.select_all()
    else:
        query.select(*properties_to_select)

    query.where(
        preset="MATCHES_REGEX",
        prop="ip",
        value=ip_regex,
    )

    if max_vcpus is not None:
        query.where(preset="LESS_THAN_OR_EQUAL_TO", prop="vcpus_used", value=max_vcpus)

    if max_vms is not None:
        query.where(preset="LESS_THAN_OR_EQUAL_TO", prop="running_vms", value=max_vms)

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

    if sort_by is not None:
        query.sort_by((sort_by, sort_direction))

    query.run(cloud_account, **kwargs)

    return {
        "to_html": query.to_html(),
        "to_string": query.to_string(),
        "to_objects": query.to_objects(),
        "to_props": query.to_props(),
    }[output_type]
