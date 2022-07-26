import datetime
from abc import ABC
from typing import Dict

from openstack.exceptions import ResourceNotFound


class ListItems(ABC):
    """
    Base class to list openstack resources

    Attributes
    ----------
    criteria_func_dict: dict
        stores generic query criteria options -
        criteria name (key) : function to evaluate generic criteria on a openstack resource(value)
                function (bool) - evaluate a generic openstack resource against a criteria

    property_func_dict: dict
        stores possible generic properties most openstack resource have
        property name (key) : function to retrieve property (value)
                function (string/int) - returns property value

    conn: (openstack.connection.Connection object)
        openstack connection object

    search_func: func()
        function that will retrieve all possible instances of an openstack resource
        (provided openstack_resource subclasses)

    Methods
    --------
    list_items(criteria_list):
        method to list openstack resources
        returns list of resouces as a Munch.munch object

    get_properties(all_items_list, property_list):
        method to get certain properties for a list of openstack resources
        returns a list of dictionaries where each dictionary represents an
        openstack resource and its values for selected properties

    """

    def __init__(self, conn, search_func):
        """constructor class"""
        self.conn = conn
        self.search_func = search_func
        self.property_func_dict: Dict
        self.criteria_func_dict = {
            "name": lambda func_dict, args: func_dict["name"] in args,
            "not_name": lambda func_dict, args: func_dict["name"] not in args,
            "name_contains": lambda func_dict, args: any(
                arg in func_dict["name"] for arg in args
            ),
            "name_not_contains": lambda func_dict, args: any(
                arg not in func_dict["name"] for arg in args
            ),
            "id": lambda func_dict, args: func_dict["id"] in args,
            "not_id": lambda func_dict, args: func_dict["id"] not in args,
        }

    def parse_criteria(self, criteria_list):
        """
        Helper function to parse and validate a list of criteria
            Parameters:
                criteria_list [(criteria name, [input_args])] : list of tuples
                containing criteria name and list of arguments
            Returns:
                a sublist of criteria from criteria_list which are valid
                for the given openstack resource being queried
        """
        res = []
        for key, args in criteria_list:

            def func(input_dict, input_key=key, input_args=args):
                return self.get_criteria_func(input_key)(input_dict, input_args)

            res.append(func)

        if not res:
            print("no criteria selected - getting all")
            res = [lambda fun_dict: True]
        return res

    def parse_properties(self, property_list):
        """
        Helper function to parse a list of properties
            Parameters:
                property_list [string] : list of property names
            Returns:
                a dictionary of {property name: function to get property} where all keys
                are a valid sublist of names from property_list
        """
        return {key: self.get_property_func(key) for key in property_list}

    def list_items(self, criteria_list):
        """
        Function to list items openstack_resource calling the function held in attribute search_func.
        Then filter openstack_resource them openstack_resource a set of criteria
            Parameters:
                criteria_list [(criteria name, [args])] : list of tuples
                containing criteria name and list of arguments
            Returns:
                [Munch.munch object] list of openstack resources
                that match all given criteria
        """
        criteria_list = self.parse_criteria(criteria_list)
        all_items = self.search_func()
        selected_items = []
        for item in all_items:
            valid_result = True
            for criteria in criteria_list:
                if not criteria(item):
                    valid_result = False
            if valid_result:
                selected_items.append(item)
        return selected_items

    def get_properties(self, all_items_list, property_list):
        """
        Function to get the selected properties from a list of openstack resources
            Parameters:
                all_items_list [Munch.munch object]: list of openstack resources
                property_list [string]: list of property names to get

            Returns:
                [fun_dict] list of dictionaries where each fun_dict contains the properties
                specified in property_list for each openstack resource in all_items_list
        """
        property_dict = self.parse_properties(property_list)

        res = []
        for item in all_items_list:
            output_dict = {}
            for key, val in property_dict.items():
                if val:
                    try:
                        output_dict[key] = val(item)
                    except ResourceNotFound:
                        output_dict[key] = "not found"
            res.append(output_dict)
        return res

    def get_criteria_func(self, key):
        """
        Helper function to get criteria function given the criteria name
        Parameters:
            key (string): criteria name
        Returns: (func) function that corresponds to criteria name
        """
        return self.criteria_func_dict.get(key, None)

    def get_property_func(self, key):
        """
        Helper function to get property function given the property name
        Parameters:
            key (string): property name
        Returns: (func) function that corresponds to property name
        """
        return self.property_func_dict.get(key, None)

    def is_older_than_x_days(
        self, created_at, days, date_time_format="%Y-%m-%dT%H:%M:%SZ"
    ):
        """
        Function to get if openstack resource is older than a given
        number of days
        Parameters:
            created_at (string): timestamp that represents date and time
            a resource was created
            days (int): number of days treshold
            date_time_format (string): date-time format of 'created_at'

        Returns: (bool) True if older than days given else False
        """
        return self.is_created_at_older_than_offset(
            created_at,
            datetime.timedelta(days=int(days)).total_seconds(),
            date_time_format,
        )

    @staticmethod
    def is_created_at_older_than_offset(
        created_at, time_offset_in_seconds, date_time_format="%Y-%m-%dT%H:%M:%SZ"
    ):
        """
        Helper function to get if openstack resource is older than a
        given number of seconds
        Parameters:
            created_at (string): timestamp that represents date and time
            a resource was created
            time_offset_in_seconds (int): number of seconds threshold
            date_time_format (string): date-time format of 'created_at'

        Returns: (bool) True if older than days given else False
        """
        offset_timestamp = (
            datetime.datetime.now()
        ).timestamp() - time_offset_in_seconds
        created_at_datetime = datetime.datetime.strptime(
            created_at, date_time_format
        ).timestamp()
        return offset_timestamp > created_at_datetime
