from enum import Enum
from typing import Tuple, Callable, Any, Dict, Optional, List
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from openstack_api.openstack_connection import OpenstackConnection

from openstack_query.utils import check_filter_func

from exceptions.parse_query_error import ParseQueryError
from tabulate import tabulate


class OpenstackQueryWrapper(OpenstackWrapperBase):

    def __init__(self, connection_cls=OpenstackConnection):

        OpenstackWrapperBase.__init__(self, connection_cls)
        self._query_props = dict()
        self._filter_func = None
        self._results_resource_objects = []
        self._results = []

    def select(self, *props: Enum):
        """
        Public method used to 'select' properties that the query will return the value of.
        Mutually exclusive to returning objects using select_all()
        :param props: one or more properties to collect described as enum
        """

        # should be a idempotent function
        # calling multiple times with should aggregate properties to select

        for prop in props:
            prop_name, prop_func = self._get_prop(prop)
            self._query_props[prop_name] = prop_func
        return self

    @staticmethod
    def _get_prop(prop: Enum) -> Tuple[str, Callable[[Any], Any]]:
        """
        static method which returns a property name and 'get_property' function for a given property enum.
        This 'get_property' function takes a Openstack resource object and returns a value which
        corresponds to the property given of that object
        """
        raise NotImplementedError("""
            This static method should be implemented in subclasses of OpenstackQueryWrapper to 
            return a tuple of 'property_name' and 'get_property' function for a given Enum representing a property
        """)

    def select_all(self):
        """
        Public method used to 'select' all properties that are available to be returned
        Mutually exclusive to returning objects using select_all()

        Overrides all currently selected properties
        returns list of properties currently selected
        """
        self._query_props = self._get_all_props()
        return self

    @staticmethod
    def _get_all_props() -> Dict[str, Callable[[Any], Any]]:
        """
        static method which returns all available 'property_name':'get_property' function key value pairs
        available.
        """
        raise NotImplementedError("""
            This static method should be implemented in subclasses of OpenstackQueryWrapper to return all available 
            tuple of 'property_name' and 'get_property' functions 
        """)

    def where(self, preset: Enum, filter_func_kwargs: Dict[str, Any]):
        """
        Public method used to set the preset that will be used to get the query filter function
        :param preset: Name of preset to use
        :param filter_func_kwargs: kwargs to pass to filter function
        """
        if self._filter_func:
            raise ParseQueryError("Error: Already set a query preset")

        filter_func = self._get_filter_func(preset)
        try:
            _ = check_filter_func(filter_func, filter_func_kwargs)
        except TypeError as func_err:
            raise ParseQueryError(f"Error parsing preset args: {func_err}")
        self._filter_func = filter_func
        return self

    @staticmethod
    def _get_filter_func(preset: Enum) -> Optional[Callable[[Any], bool]]:
        """
        static method that is used to return a filter function for given preset, if any
        :param preset: A given preset that describes the query type
        """
        raise NotImplementedError("""
            This static method should be implemented in subclasses of OpenstackQueryWrapper to return a filter_function 
            for a given preset Enum 
        """)

    def sort_by(self, sort_by: Enum, reverse=False):
        """
        Public method used to configure sorting results
        :param sort_by: name of property to sort by
        :param reverse: False is sort by ascending, True is sort by descending, default False
        """
        raise NotImplementedError

    def group_by(self, group_by: Enum):
        """
        Public method used to configure grouping results.
        :param group_by: name of the property to group by
        """
        raise NotImplementedError

    def run(self, cloud_account: str, **kwargs):
        """
        Public method that runs the query provided that it has been configured properly
        :param cloud_account: The account from the clouds configuration to use
        :param kwargs: keyword args that can be used to configure details of how query is run
            - valid kwargs specific to resource
        """

        if len(self._query_props) == 0:
            raise RuntimeError("""
                query ran but no properties selected use select() method to 
                set properties or select_all() to select all available properties
            """)

        with self._connection_cls(cloud_account) as conn:
            self._results_resource_objects = self._run_query(conn, **kwargs)

        self._results_resource_objects = self._apply_filter_func(
            self._results_resource_objects,
            self._filter_func,
        )

        # TODO: sort by and group by here
        self._results = self._parse_properties(
            self._results_resource_objects,
            self._query_props
        )

        return self

    @staticmethod
    def _parse_properties(
            items: List[Any],
            property_funcs: Dict[str, Callable[[Any], Any]],
    ) -> List[Dict]:
        """
        Generates a dictionary of queried properties from a list of openstack objects e.g. servers
        :param items: List of items to obtain properties from
        :param property_funcs: property_functions that return properties requested
        :return: List containing dictionaries of the requested properties obtained from the items
        """
        return [OpenstackQueryWrapper._parse_property(item, property_funcs) for item in items]

    @staticmethod
    def _parse_property(item: Any, property_funcs: Dict[str, Callable[[Any], Any]]):
        """
        Generates a dictionary of queried properties from a single openstack object
        :param item: openstack resource item to obtain properties from
        :param property_funcs: Dict of 'property_name' 'property_function' key value pairs
        """
        return {
            prop_key: OpenstackQueryWrapper._run_prop_func(item, prop_func, default_out="Not Found") for prop_key, prop_func in property_funcs.items()
        }

    @staticmethod
    def _run_prop_func(item: Any, prop_func: Callable[[Any], Any], default_out="Not Found"):
        """
        Runs a function to get a property for a given openstack resource
        :param item: openstack resource item to obtain property from
        :param prop_func: A 'property_function' to return the property of an openstack resource
        :param default_out: A default to set if the property cannot be found on the resource
        """
        try:
            return str(prop_func(item))
        except AttributeError:
            return default_out

    @staticmethod
    def _apply_filter_func(items: List[Any], query_func: Callable[[Any], bool]) -> List[Any]:
        """
        Removes items from a list by running a given query function
        :param items: List of items to query e.g. list of servers
        :param query_func: Query function that determines whether a given item
                           matches the query - should return true if it passes
                           the query
        :return: List of items that match the given query
        """
        return [item for item in items if query_func(item)]

    @staticmethod
    def _run_query(self, conn: OpenstackConnection, **kwargs):
        """
        This method is to be instantiated in subclasses of this class to run openstack query command
        """
        raise NotImplementedError("""
            This static method should be implemented in subclasses of OpenstackQueryWrapper to 
            run the appropriate openstack command(s)
        """)

    def to_list(self, as_objects=False):
        """
        Public method to return results as a list
        :param as_objects: whether to return a list of openstack objects, or a list of dictionaries containing selected properties
        """
        return self._results_resource_objects if as_objects else self._results

    def to_string(self, **kwargs):
        """
        Public method to return results as a table
        :param kwargs: kwargs to pass to generate table
        """
        return self._generate_table(self._results, return_html=False, **kwargs)

    def to_html(self, **kwargs):
        """
        Public method to return results as html table
        :param kwargs: kwargs to pass to generate table
        """
        return self._generate_table(self._results, return_html=True, **kwargs)

    @staticmethod
    def _generate_table(
            properties_dict: List[Dict[str, Any]],
            return_html: bool,
            **kwargs
    ) -> str:
        """
        Returns a table from the result of 'self._parse_properties'
        :param properties_dict: dict of query results
        :param return_html: True if output required in html table format else output plain text table
        :param kwargs: kwargs to pass to tabulate
        :return: String (html or plaintext table of results)
        """
        headers = properties_dict[0].keys()
        rows = [row.values() for row in properties_dict]
        return tabulate(rows, list(headers), tablefmt="html" if return_html else "grid", **kwargs)
