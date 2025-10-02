from typing import List, Optional

import openstackquery
from workflows.to_webhook import to_webhook

# pylint:disable=too-many-arguments


def search_by_expression(
    cloud_account: str,
    query_type: str,
    search_mode: str,
    property_to_search_by: str,
    value: int,
    properties_to_select: Optional[List[str]] = None,
    output_type: Optional[str] = None,
    group_by: Optional[str] = None,
    sort_by: Optional[List[str]] = None,
    webhook: Optional[str] = None,
    **kwargs
):
    """
    Method that builds and runs a query to find generic numerical resource based on a expression
    (less-than, greater-than etc)
    :param cloud_account: A string representing the cloud account to use - set in clouds.yaml
    :param query_type: what Query object to use to run query with ServerQuery, UserQuery etc
    :param search_mode: A string representing a preset Enum
        LESS_THAN,
        LESS_THAN_OR_EQUAL_TO,
        GREATE_THAN,
        GREATER_THAN_OR_EQUAL_TO
    which dictates what query to perform
    :param property_to_search_by: A string representing a datetime property Enum that the preset will be used on
    :param value: A number to compare property against
    :param properties_to_select: list of strings representing which properties to select
    :param output_type: string representing how to output the query
    :param group_by: an optional string representing a property to group results by
    :param sort_by: an optional set of tuples representing way which properties to sort results by
    :param webhook: an Optional string representing a stackstorm webhook url path, can't be used alongside group_by
    :param kwargs: A set of optional meta params to pass to the query
    """

    query = getattr(openstackquery, query_type)()
    if not properties_to_select:
        query.select_all()
    else:
        query.select(*properties_to_select)

    query.where(
        preset=search_mode,
        prop=property_to_search_by,
        value=value,
    )

    if sort_by:
        query.sort_by(*[(p, "desc") for p in sort_by])
    if group_by:
        query.group_by(group_by)

    query.run(cloud_account, **kwargs)

    if webhook:
        to_webhook(webhook=webhook, payload=query.to_props())

    # pylint: disable=unnecessary-lambda
    return {
        "to_html": lambda: query.to_html(),
        "to_string": lambda: query.to_string(),
        "to_objects": lambda: query.to_objects(),
        "to_props": lambda: query.to_props(),
        "to_csv": lambda: query.to_csv(),
        "to_json": lambda: query.to_json(),
    }[output_type]()
