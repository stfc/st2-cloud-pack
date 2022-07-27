import datetime
from typing import Any, Callable, Dict, List
from tabulate import tabulate

from openstack_api.openstack_identity import OpenstackIdentity


class OpenstackQuery:
    @staticmethod
    def apply_query(items: List, query_func: Callable[[Any], bool]) -> List:
        """
        Removes items from a list by running a given query function
        :param items: List of items to query e.g. list of servers
        :param query_func: Query function that determines whether a given item
                           matches the query - should return true if it passes
                           the query
        :return: List of items that match the given query
        """
        for item in items:
            if not query_func(item):
                items.remove(item)
        return items

    @staticmethod
    def datetime_before_x_days(
        value: str, days, date_time_format: str = "%Y-%m-%dT%H:%M:%SZ"
    ) -> bool:
        """
        Function to get if openstack resource is older than a given
        number of days
        Parameters:
            value (string): timestamp that represents date and time
            a resource was created
            days (int): number of days treshold
            date_time_format (string): date-time format of 'created_at'

        Returns: (bool) True if older than days given else False
        """
        return OpenstackQuery.datetime_older_than_offset(
            value,
            datetime.timedelta(days=int(days)).total_seconds(),
            date_time_format,
        )

    @staticmethod
    def datetime_older_than_offset(
        value: str,
        time_offset_in_seconds: int,
        date_time_format: str = "%Y-%m-%dT%H:%M:%SZ",
    ) -> bool:
        """
        Helper function to get if openstack resource is older than a
        given number of seconds
        Parameters:
            value (string): timestamp that represents date and time
            a resource was created
            time_offset_in_seconds (int): number of seconds threshold
            date_time_format (string): date-time format of 'created_at'

        Returns: (bool) True if older than days given else False
        """
        offset_timestamp = (
            datetime.datetime.now()
        ).timestamp() - time_offset_in_seconds
        value_datetime = datetime.datetime.strptime(value, date_time_format).timestamp()
        return offset_timestamp > value_datetime

    @staticmethod
    def parse_properties(
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

    @staticmethod
    def generate_table(properties_dict: List[Dict[str, Any]], get_html: bool) -> str:
        """
        Returns a table from the result of 'parse_properties'
        :param properties_dict: dict of query results
        :param get_html: True if output required in html table format else output plain text table
        :return: String (html or plaintext table of results)
        """
        headers = properties_dict[0].keys()
        rows = [row.values() for row in properties_dict]
        return tabulate(rows, headers, tablefmt="html" if get_html else "grid")

    @staticmethod
    def collate_results(
        properties_dict: List[Dict[str, Any]], key: str, get_html: bool
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
            print(f"Following items found with no associated key '{key}'")
            print(OpenstackQuery.generate_table(collated_dict[None], False))
            del collated_dict[None]

        for key_value, items in collated_dict.items():
            collated_dict[key_value] = OpenstackQuery.generate_table(items, get_html)

        return collated_dict

    @staticmethod
    def get_default_property_funcs(
        object_type: str, cloud_account: str, identity_api: OpenstackIdentity
    ) -> Dict[str, Callable[[Any], bool]]:
        """
        Returns a list of default property functions for use with 'parse_properties' above
        :param object_type: type of openstack object the functions will be used for e.g. server
        :return: Dict[str, str] (each key containing html or plaintext table of results)
        """
        if object_type == "server":
            return {
                "user_email": lambda a: identity_api.find_user_all_domains(
                    cloud_account, a["user_id"]
                )["email"],
                "user_name": lambda a: identity_api.find_user_all_domains(
                    cloud_account, a["user_id"]
                )["name"],
            }
        raise ValueError(f"Unsupported object type '{object_type}'")
