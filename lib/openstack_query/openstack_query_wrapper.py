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
        raise NotImplementedError

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
