import re
from typing import List, Optional

from apis.openstack_api.openstack_connection import OpenstackConnection
from apis.openstack_api.openstack_hypervisor import get_available_flavors
from openstack.connection import Connection
from openstackquery import HypervisorQuery, ServerQuery

# pylint:disable=too-many-arguments
# pylint:disable=too-many-locals


def find_reinstall_candidate_hypervisors(
    cloud_account: str,
    ip_regex: str,
    max_vcpus: Optional[int] = None,
    max_vms: Optional[int] = None,
    include_down: Optional[bool] = False,
    include_disabled: Optional[bool] = False,
    exclude_hostnames: Optional[List[str]] = None,
    include_flavours: Optional[List[str]] = None,
    exclude_flavours: Optional[List[str]] = None,
    output_type: Optional[str] = "to_string",
    sort_by: Optional[str] = "vcpus_used",
    sort_direction: Optional[str] = "asc",
    **kwargs,
):
    """
    Finds candidate hypervisors for reinstallation based on resource usage,
    hostname/IP filtering, and allowed or disallowed flavor types.

    :param cloud_account: A string representing the cloud account to use - set in clouds.yaml
    :param ip_regex: Regular expression pattern to filter hypervisor IPs (default: "172.16.x.x").
    :param max_vcpus: Optional maximum threshold for used vCPUs.
    :param max_vms: Optional maximum threshold for running VMs.
    :param include_down: Optional boolean to include hypervisors with state "down"
    :param include_disabled: Optional boolean to include hypervisors with status "disabled"
    :param exclude_hostnames: Optional list of hypervisor hostname substrings to exclude.
    :param include_flavours: Optional list of flavor names; only hypervisors that support at least one are included.
    :param exclude_flavours: Optional list of flavor names; hypervisors that support any of these are excluded.
    :param output_type: string representing desired output type of the query
    :param sort_by: Optional property to sort the results by.
    :param sort_direction: Sort direction for the results; either "asc" or "desc" (default: "desc").
    :param kwargs: A set of optional meta params to pass to the query

    :return: Query result in the specified output format.
    """

    query = HypervisorQuery()
    # Hardcoded to simplify process, additional values can be found via hypervisor query if desired
    properties_to_select = [
        "id",
        "ip",
        "memory_free",
        "memory",
        "memory_used",
        "name",
        "state",
        "status",
        "vcpus",
        "vcpus_used",
        "disabled_reason",
    ]

    query.select(*properties_to_select)

    query.where(
        preset="MATCHES_REGEX",
        prop="ip",
        value=ip_regex,
    )

    if max_vcpus is not None:
        query.where(preset="LESS_THAN_OR_EQUAL_TO", prop="vcpus_used", value=max_vcpus)

    if not include_down:
        query.where(preset="EQUAL_TO", prop="state", value="up")

    if not include_disabled:
        query.where(preset="EQUAL_TO", prop="status", value="enabled")

    if exclude_hostnames:
        query.where(
            preset="NOT_MATCHES_REGEX",
            prop="name",
            value=construct_hostname_regex(exclude_hostnames),
        )

    if sort_by and sort_by != "running_vms":
        query.sort_by((sort_by, sort_direction))

    if include_flavours or exclude_flavours:
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
    query.run(cloud_account, **kwargs)

    # pylint: disable=protected-access
    hypervisor_results = query.results_container._results

    server_query = ServerQuery()
    server_query.group_by("hypervisor_name")
    server_query.run(cloud_account, all_projects=True, as_admin=True)
    servers_grouped = server_query.to_props()

    for hv_result in hypervisor_results:
        hv_name = hv_result.get_prop(hv_result._prop_enum_cls.HYPERVISOR_NAME)
        running_vms_count = len(servers_grouped.get(hv_name, []))
        hv_result.update_forwarded_properties({"running_vms": running_vms_count})

    if max_vms is not None:
        filtered_results = [
            r
            for r in hypervisor_results
            if r._forwarded_props.get("running_vms", 0) <= max_vms
        ]
        query.results_container._results = filtered_results
        query.results_container._parsed_results = []

    if sort_by == "running_vms":
        query.results_container._results.sort(
            key=lambda result: result._forwarded_props.get("running_vms", 0),
            reverse=(sort_direction != "asc"),
        )

    query.results_container._parsed_results = query.results_container._results

    # pylint: disable=unnecessary-lambda
    return {
        "to_html": lambda: query.to_html(),
        "to_string": lambda: query.to_string(),
        "to_objects": lambda: query.to_objects(),
        "to_props": lambda: query.to_props(),
        "to_csv": lambda: query.to_csv(),
        "to_json": lambda: query.to_json(),
    }[output_type]()


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


def construct_hostname_regex(exclude_hostnames: List[str]) -> str:
    escaped_hostnames = [re.escape(h) for h in exclude_hostnames]
    return f".*(?:{'|'.join(escaped_hostnames)})"
