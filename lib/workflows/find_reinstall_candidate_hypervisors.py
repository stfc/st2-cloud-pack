import re
from typing import List, Optional

from openstack.connection import Connection
from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_hypervisor import get_available_flavors
from openstackquery import HypervisorQuery

# pylint:disable=too-many-arguments
# pylint:disable=too-many-locals


def find_reinstall_candidate_hypervisors(
    cloud_account: str,
    ip_regex: Optional[str] = r"^172\.16\.(?:\d{1,3})\.(?:\d{1,3})$",
    max_vcpus: Optional[int] = None,
    max_vms: Optional[int] = None,
    exclude_hostnames: Optional[List[str]] = None,
    include_flavours: Optional[List[str]] = None,
    exclude_flavours: Optional[List[str]] = None,
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
    :param include_flavours: Optional list of flavor names; only hypervisors that support at least one are included.
    :param exclude_flavours: Optional list of flavor names; hypervisors that support any of these are excluded.
    :param properties_to_select: Optional list of strings representing which properties to select,
    else all are selected.
    :param output_type: string representing desired output type of the query
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
        query.where(
            preset="MATCHES_REGEX",
            prop="name",
            value=construct_hostname_exclude_regex(exclude_hostnames),
        )

    if sort_by is not None:
        query.sort_by((sort_by, sort_direction))

    if include_flavours or exclude_flavours:
        if "name" not in properties_to_select:
            query.select("name", *properties_to_select)

        query.run(cloud_account, **kwargs)
        hvs = query.to_props(flatten=True)

        with OpenstackConnection(cloud_account) as conn:
            allowed_hv_names = filter_hypervisors_by_flavour(
                conn, hvs["hypervisor_name"], include_flavours, exclude_flavours
            )

        query.where(
            preset="ANY_IN",
            prop="name",
            value=allowed_hv_names,
        )

        if "name" not in properties_to_select:
            query.select(*properties_to_select)

    query.run(cloud_account, **kwargs)

    return {
        "to_html": query.to_html(),
        "to_string": query.to_string(),
        "to_objects": query.to_objects(),
        "to_props": query.to_props(),
    }[output_type]


def filter_hypervisors_by_flavour(
    conn: Connection,
    hv_names: List[str],
    include_flavours: Optional[List[str]],
    exclude_flavours: Optional[List[str]],
) -> List[str]:
    def check_flavours_allowed(conn, hv_name):
        flavours = set(get_available_flavors(conn, hv_name))

        if include_flavours:
            if not set(include_flavours).intersection(flavours):
                return False

        if exclude_flavours:
            if set(exclude_flavours).intersection(flavours):
                return False

        return True

    allowed_hv_names = [name for name in hv_names if check_flavours_allowed(conn, name)]

    return allowed_hv_names


def construct_hostname_exclude_regex(exclude_hostnames: List[str]) -> str:
    escaped_hostnames = [re.escape(h) for h in exclude_hostnames]
    return f"^(?!.*({'|'.join(escaped_hostnames)})).*$"
