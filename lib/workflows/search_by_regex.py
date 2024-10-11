from typing import List, Optional
from enums.query.query_presets import QueryPresetsString
from enums.query.sort_order import SortOrder
import openstack_query
from workflows.to_webhook import to_webhook

# pylint:disable=too-many-arguments


def search_by_regex(
    cloud_account: str,
    query_type: str,
    property_to_search_by: str,
    pattern: str,
    properties_to_select: Optional[List[str]] = None,
    output_type: Optional[str] = None,
    group_by: Optional[str] = None,
    sort_by: Optional[List[str]] = None,
    webhook: Optional[str] = None,
    **kwargs,
):
    """
    method that builds and runs a query to find generic resource with a property matching regex.
    :param cloud_account: A string representing the cloud account to use - set in clouds.ymal
    :param query_type: what Query object to use to run query with ServerQuery, UserQuery etc
    :param property_to_search_by: A string representing a string property Enum that the preset will be used on
    :param pattern: A string representing a regex pattern
    :param properties_to_select: list of strings representing which properties to select
    :param output_type: string representing how to output the query
    :param group_by: an optional string representing a property to group results by
    :param sort_by: an optional set of tuples representing way which properties to sort results by
    :param webhook: an Optional string representing a stackstorm webhook url path, can't be used alongside group_by
    :param kwargs: A set of optional meta params to pass to the query
    """

    query = getattr(openstack_query, query_type)()
    if not properties_to_select:
        query.select_all()
    else:
        query.select(*properties_to_select)

    query.where(
        preset=QueryPresetsString.MATCHES_REGEX,
        prop=property_to_search_by,
        value=pattern,
    )

    if sort_by:
        query.sort_by(*[(p, SortOrder.DESC) for p in sort_by])
    if group_by:
        query.group_by(group_by)

    query.run(cloud_account, **kwargs)

    if webhook:
        to_webhook(webhook=webhook, payload=query.to_props())

    return {
        "to_html": query.to_html(),
        "to_string": query.to_string(),
        "to_objects": query.to_objects(),
        "to_props": query.to_props(),
    }[output_type]
