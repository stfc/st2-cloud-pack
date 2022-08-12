import datetime
from typing import Any, Callable, Dict, List
from tabulate import tabulate
from openstack_api.openstack_connection import OpenstackConnection

from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase


class OpenstackQuery(OpenstackWrapperBase):

    # Various queries useful for openstack objects
    def query_datetime_before(self, prop: str, days: int):
        """
        Returns a query for checking if a datetime property is before a specified
        number of days in the past
        """
        return lambda a: self.datetime_before_x_days(a[prop], days)

    def query_datetime_after(self, prop: str, days: int):
        """
        Returns a query for checking if a datetime property is after a specified
        number of days in the past
        """
        return lambda a: not self.datetime_before_x_days(a[prop], days)

    def query_prop_in(self, prop: str, values: List[str]):
        """
        Returns a query for checking if a property value is within a list of values
        """
        return lambda a: a[prop] in values

    def query_prop_not_in(self, prop: str, values: List[str]):
        """
        Returns a query for checking if a property value is not within a list of values
        """
        return lambda a: a[prop] not in values

    def query_prop_contains(self, prop: str, snippets: List[str]):
        """
        Returns a query for checking if a property value contains all the snippets given in
        a list
        """
        return lambda a: all(snippet in a[prop] for snippet in snippets)

    def query_prop_not_contains(self, prop: str, snippets: List[str]):
        """
        Returns a query for checking if a property value does not contain all the snippets
        given in a list
        """
        return lambda a: all(snippet not in a[prop] for snippet in snippets)

    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(connection_cls)

    def apply_query(self, items: List, query_func: Callable[[Any], bool]) -> List:
        """
        Removes items from a list by running a given query function
        :param items: List of items to query e.g. list of servers
        :param query_func: Query function that determines whether a given item
                           matches the query - should return true if it passes
                           the query
        :return: List of items that match the given query
        """
        return [item for item in items if query_func(item)]

    def apply_queries(
        self, items: List, query_funcs: List[Callable[[Any], bool]]
    ) -> List:
        """
        Removes items from a list by running a set of given query function
        :param items: List of items to query e.g. list of servers
        :param query_funcs: List of query functions that determines whether a given item
                           matches the query - should return true if it passes
                           the query
        :return: List of items that match the given queries
        """
        result = items
        for query_func in query_funcs:
            result = self.apply_query(items=result, query_func=query_func)
        return result

    def datetime_before_x_days(
        self, value: str, days: int, date_time_format: str = "%Y-%m-%dT%H:%M:%SZ"
    ) -> bool:
        """
        Function to get if openstack resource is older than a given
        number of days
        Parameters:
            value (string): timestamp that represents date and time
            a resource was created
            days (int): number of days threshold
            date_time_format (string): date-time format of 'created_at'

        Returns: (bool) True if older than days given else False
        """
        return self.datetime_older_than_offset(
            value,
            datetime.timedelta(days=days).total_seconds(),
            date_time_format,
        )

    def datetime_older_than_offset(
        self,
        value: str,
        time_offset_in_seconds: float,
        date_time_format: str = "%Y-%m-%dT%H:%M:%SZ",
    ) -> bool:
        """
        Helper function to get if openstack resource is older than a
        given number of seconds
        Parameters:
            value (string): timestamp that represents date and time
            a resource was created
            time_offset_in_seconds (float): number of seconds threshold
            date_time_format (string): date-time format of 'created_at'

        Returns: (bool) True if older than days given else False
        """
        offset_timestamp = (
            datetime.datetime.now()
        ).timestamp() - time_offset_in_seconds
        value_datetime = datetime.datetime.strptime(value, date_time_format).timestamp()
        return offset_timestamp > value_datetime

    def parse_properties(
        self,
        items: List,
        properties_to_list: List[str],
        property_funcs: Dict[str, Callable[[Any], Any]],
    ) -> List[Dict]:
        """
        Generates a dictionary of queried properties from a list of openstack objects e.g. servers
        :param items: List of items to obtain properties from
        :param properties_to_list: List of properties to obtain from the items
        :param property_funcs: Query functions that return properties requested in 'properties_to_list'
        :return: List containing dictionaries of the requested properties obtained from the items
        """
        output = []
        for item in items:
            item_output = {}
            for prop in properties_to_list:
                # If the property func is listed then use that, otherwise assume can obtain from the object directly
                if prop in property_funcs:
                    property_value = property_funcs[prop](item)
                else:
                    try:
                        property_value = item[prop]
                    except AttributeError:
                        property_value = "Not found"

                item_output[prop] = property_value
            output.append(item_output)
        return output

    def generate_table(
        self, properties_dict: List[Dict[str, Any]], get_html: bool
    ) -> str:
        """
        Returns a table from the result of 'parse_properties'
        :param properties_dict: dict of query results
        :param get_html: True if output required in html table format else output plain text table
        :return: String (html or plaintext table of results)
        """
        headers = properties_dict[0].keys()
        rows = [row.values() for row in properties_dict]
        return tabulate(rows, headers, tablefmt="html" if get_html else "grid")

    def collate_results(
        self, properties_dict: List[Dict[str, Any]], key: str, get_html: bool
    ) -> Dict[str, str]:
        """
        Collates results from a dict based on a given property key and returns a dictionary of
        these keys with tables of the properties
        :param properties_dict: dict of query results
        :param key: key to collate by e.g. user_email
        :param get_html: True if output required in html table format else output plain text table
        :return: Dict[str, str] (each key containing html or plaintext table of results)
        """
        collated_dict = {}
        for item in properties_dict:
            key_value = item[key]
            if key_value in collated_dict:
                collated_dict[key_value].append(item)
            else:
                collated_dict[key_value] = [item]

        if None in collated_dict:
            print(f"The following items were found with no associated key '{key}'")
            print(self.generate_table(collated_dict[None], False))
            del collated_dict[None]

        for key_value, items in collated_dict.items():
            collated_dict[key_value] = self.generate_table(items, get_html)

        return collated_dict

    def get_default_property_funcs(
        self, object_type: str, cloud_account: str
    ) -> Dict[str, Callable[[Any], bool]]:
        """
        Returns a list of default property functions for use with 'parse_properties' above
        :param object_type: type of openstack object the functions will be used for e.g. server
        :param cloud_account: The account from the clouds configuration to use
        :return: Dict[str, str] (each key containing html or plaintext table of results)
        """

        def get_project_prop(project_id, prop):
            project = self._identity_api.find_project(cloud_account, project_id)
            if project:
                return project[prop]
            return None

        if object_type == "server":
            return {
                "user_email": lambda a: self._identity_api.find_user_all_domains(
                    cloud_account, a["user_id"]
                )["email"],
                "user_name": lambda a: self._identity_api.find_user_all_domains(
                    cloud_account, a["user_id"]
                )["name"],
            }
        if object_type == "floating_ip":
            return {
                "project_name": lambda a: get_project_prop(a["project_id"], "name"),
                "project_email": lambda a: self._identity_api.find_project_email(
                    cloud_account, a["project_id"]
                ),
            }
        raise ValueError(f"Unsupported object type '{object_type}'")

    # pylint:disable=too-many-arguments
    def parse_and_output_table(
        self,
        cloud_account: str,
        items: List,
        object_type: str,
        properties_to_select: List[str],
        group_by: str,
        get_html: bool,
    ):
        """
        Finds all servers belonging to a project (or all servers if project is empty)
        :param cloud_account: The account from the clouds configuration to use
        :param object_type: type of openstack object the functions will be used for e.g. server
        :param properties_to_select: The list of properties to select and output from the found servers
        :param group_by: Property to group returned results - can be empty for no grouping
        :param get_html: When True tables returned are in html format
        :return: (String or Dictionary of strings) Table(s) of results grouped by the 'group_by' parameter
        """

        property_funcs = self.get_default_property_funcs(object_type, cloud_account)
        output = self.parse_properties(items, properties_to_select, property_funcs)

        if len(output) == 0:
            return None

        if group_by != "":
            output = self.collate_results(output, group_by, get_html)
        else:
            output = self.generate_table(output, get_html)

        return output
