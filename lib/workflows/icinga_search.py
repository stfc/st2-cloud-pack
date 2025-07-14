import json
from functools import partial
from typing import Callable, Dict, List, Optional

from apis.icinga_api.enums.icinga_states import HostState, ServiceState
from apis.icinga_api.query_objects import IcingaQuery, query_object
from apis.icinga_api.structs.icinga_account import IcingaAccount
from tabulate import tabulate


def create_join_filter_functions(user_joins: List[str]) -> List[Callable[[Dict], str]]:
    """
    Parses list of user defined joins and returns a list of filter
    functions to return respective value for each join.
    :param user_joins: List of user defined joins
    """

    def get_value(a: Dict, filter1: str, filter2: str, states=None) -> str:
        """
        Returns a value from a nested dictionary
        :param a: Dictionary to return value from
        :param filter1: First dictionary key to filter by
        :param filter2: Second dictionary key to filter by
        :param states: Enum to convert host/service state from int value to string
        :return: Value of the key filtered for
        """
        value = a["joins"][filter1][filter2]
        return states(value).name if states else value

    filter_functions = []
    for join in user_joins:
        filter1, filter2 = join.split(".")
        states = (
            (ServiceState if filter1 == "service" else HostState)
            if filter2 == "state"
            else None
        )
        filter_functions.append(
            partial(get_value, filter1=filter1, filter2=filter2, states=states)
        )

    return filter_functions


def create_property_filter_functions(
    object_type: str, propeties: List[str]
) -> List[Callable[[Dict], str]]:
    """
    Parses list of user defined propeties and returns a list of filter
    functions to return respective value for each join.
    :param object_type: Type of object in Icinga
    :param propeties: List of user defined propeties
    """

    def get_value(a: Dict, filter1: str, states=None) -> str:
        """
        Returns a value from a dictionary
        :param a: Dictionary to return value from
        :param filter1: First dictionary key to filter by
        :param states: Enum to convert host/service state from int value to string
        :return: Value of the key filtered for
        """
        value = a["attrs"][filter1]
        return states(value).name if states else value

    filter_functions = []
    for prop in propeties:
        states = (
            (ServiceState if object_type == "Service" else HostState)
            if prop == "state"
            else None
        )
        filter_functions.append(partial(get_value, filter1=prop, states=states))

    return filter_functions


def generate_table(
    data: Dict, object_type: str, properties_to_select: List[str], user_joins: List[str]
) -> str:
    """
    Generate a table of properties from the query results
    :param data: results of the query in a dict
    :param object_type: Type of iginga object
    :param properties_to_select: User defined properties returned by the query
    :param user_joins: User defined query joins
    :return: tabulate table string
    """
    results = []
    prop_filter_functions = create_property_filter_functions(
        object_type, properties_to_select
    )
    join_filter_functions = (
        create_join_filter_functions(user_joins) if user_joins is not None else []
    )

    for host in data["results"]:
        props = [fn(host) for fn in prop_filter_functions]
        joins = [fn(host) for fn in join_filter_functions]

        props += joins
        results.append(props)

    headers = []
    for prop in properties_to_select:
        headers.append((f"{object_type} {prop}").title())
    for join in user_joins if user_joins is not None else []:
        join = join.replace(".", " ")
        headers.append(join.title())

    return tabulate(tabular_data=results, headers=headers, tablefmt="grid")


def search_by_state(
    icinga_account: IcingaAccount,
    object_type: str,
    state: str,
    output_type: str,
    properties_to_select: List[str],
    joins: Optional[List[str]] = None,
):
    """
    Query iginga for objects in a given state
    :param icinga_account: Account used to interact with icinga
    :param object_type: Type of iginga object
    :param state: Host/Service state to filter by
    :param output_type: how to output the query
    :param properties_to_select: User defined properties returned by the query
    :param user_joins: User defined query joins
    """

    state = (
        HostState[state.upper()]
        if object_type == "Host"
        else ServiceState[state.upper()]
    )

    query = IcingaQuery(
        object_type=object_type,
        filter=f"host.vars.team==team && {object_type.lower()}.state==state",
        filter_vars={"team": "cloud", "state": state.value},
        properties_to_select=properties_to_select,
        joins=joins,
    )

    _, data = query_object(icinga_account, query)

    data = json.loads(data)

    return {
        "dict": data,
        "table": generate_table(data, object_type, properties_to_select, joins),
    }[output_type]


def search_by_name(
    icinga_account: IcingaAccount,
    object_type: str,
    name: str,
    output_type: str,
    properties_to_select: List[str],
    joins: Optional[List[str]] = None,
):
    """
    Query iginga for objects in a given state
    :param icinga_account: Account used to interact with icinga
    :param object_type: Type of iginga object
    :param name: name of iginga object, can be regex pattern
    :param output_type: how to output the query
    :param properties_to_select: User defined properties returned by the query
    :param user_joins: User defined query joins
    """
    query = IcingaQuery(
        object_type=object_type,
        filter=f"host.vars.team==team && match(pattern, {object_type.lower()}.name)",
        filter_vars={"team": "cloud", "pattern": name},
        properties_to_select=properties_to_select,
        joins=joins,
    )

    _, data = query_object(icinga_account, query)

    data = json.loads(data)

    return {
        "dict": data,
        "table": generate_table(data, object_type, properties_to_select, joins),
    }[output_type]
