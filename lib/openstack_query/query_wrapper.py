from enum import Enum
from typing import Tuple, Callable, Any, Dict, Optional, List, Union
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from openstack_api.openstack_connection import OpenstackConnection

from openstack_query.utils import (
    check_filter_func,
    check_kwarg_mapping,
    prop_equal_to,
    prop_not_equal_to,
    prop_greater_than,
    prop_less_than,
    prop_younger_than,
    prop_older_than,
    prop_older_than_or_equal_to,
    prop_younger_than_or_equal_to,
    prop_any_in,
    prop_not_any_in,
    prop_matches_regex,
)


from exceptions.parse_query_error import ParseQueryError
from exceptions.query_mapping_error import QueryMappingError

from enums.query.query_presets import QueryPresets
from tabulate import tabulate


class QueryWrapper(OpenstackWrapperBase):
    _PROPERTY_MAPPINGS = {}
    _KWARG_MAPPINGS = {}
    _NON_DEFAULT_FILTER_FUNCTION_MAPPINGS = {}
    _DEFAULT_FILTER_FUNCTION_MAPPINGS = {}
    _DEFAULT_FILTER_FUNCTIONS = {
        QueryPresets.EQUAL_TO: prop_equal_to,
        QueryPresets.NOT_EQUAL_TO: prop_not_equal_to,
        QueryPresets.GREATER_THAN: prop_greater_than,
        QueryPresets.LESS_THAN: prop_less_than,
        QueryPresets.YOUNGER_THAN: prop_younger_than,
        QueryPresets.YOUNGER_THAN_OR_EQUAL_TO: prop_younger_than_or_equal_to,
        QueryPresets.OLDER_THAN_OR_EQUAL_TO: prop_older_than_or_equal_to,
        QueryPresets.OLDER_THAN: prop_older_than,
        QueryPresets.ANY_IN: prop_any_in,
        QueryPresets.NOT_ANY_IN: prop_not_any_in,
        QueryPresets.MATCHES_REGEX: prop_matches_regex,
    }

    def __init__(self, connection_cls=OpenstackConnection):
        OpenstackWrapperBase.__init__(self, connection_cls)
        self._query_props = dict()
        self._filter_func = None
        self._filter_kwargs = None
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

    def _get_prop(self, prop: Enum) -> Tuple[str, Callable[[Any], Any]]:
        """
        static method which returns a property name and 'get_property' function for a given property enum.
        This 'get_property' function takes a Openstack resource object and returns a value which
        corresponds to the property given of that object
        """
        if prop not in self._PROPERTY_MAPPINGS.keys():
            raise QueryMappingError(
                """
                Error: failed to get property mapping, the property is valid
                but does not contain an entry in PROPERTY_MAPPINGS.
                Please raise an issue with repo maintainer
            """
            )
        return prop.name.lower(), self._PROPERTY_MAPPINGS[prop]

    def select_all(self):
        """
        Public method used to 'select' all properties that are available to be returned
        Mutually exclusive to returning objects using select_all()

        Overrides all currently selected properties
        returns list of properties currently selected
        """
        self._query_props = self._get_all_props()
        return self

    def _get_all_props(self) -> Dict[str, Callable[[Any], Any]]:
        """
        static method which returns all available 'property_name':'get_property' function key value pairs
        available.
        """
        return {k.name.lower(): v for k, v in self._PROPERTY_MAPPINGS.items()}

    def where(self, preset: QueryPresets, prop: Enum, preset_args: Dict[str, Any]):
        """
        Public method used to set the preset that will be used to get the query filter function
        :param preset: Name of query preset to use
        :param prop: Property that the query preset will be used on
        :param preset_args: kwargs to pass to filter function
        """
        if self._filter_func:
            raise ParseQueryError("Error: Already set a query preset")

        self._filter_kwargs = self._parse_kwargs(preset, prop, preset_args)
        self._filter_func = self._parse_filter_func(preset, prop, preset_args)

        return self

    def _parse_kwargs(
        self, preset: QueryPresets, prop: Enum, preset_args: Dict[str, Any]
    ):
        kwarg_mapping = self._get_kwarg(preset, prop)
        if kwarg_mapping:
            check_kwarg_mapping(kwarg_mapping, preset_args)
            return kwarg_mapping(**preset_args)
        return None

    def _parse_filter_func(
        self, preset: QueryPresets, prop: Enum, preset_args: Dict[str, Any]
    ):
        filter_func = self._get_filter_func(preset, prop)
        try:
            preset_args.update({"prop": prop})
            _ = check_filter_func(filter_func, preset_args)
        except TypeError as func_err:
            raise ParseQueryError(f"Error parsing preset args: {func_err}")
        return filter_func

    def _get_kwarg(
        self, preset: QueryPresets, prop: Enum
    ) -> Optional[Callable[[Any], str]]:
        """
        returns a dict containing filter kwargs to pass to openstack command to get all resources if mapping exists for
        a given preset, property pair
        :param preset: A given preset that describes the query type
        :param prop: A given prop that we want base the query on
        """

        if preset in self._KWARG_MAPPINGS.keys():
            return self._KWARG_MAPPINGS[preset].get(prop, None)
        return None

    def _get_filter_func(
        self, preset: QueryPresets, prop: Enum
    ) -> Optional[Callable[[Any], bool]]:
        """
        Method that is used to return a filter function for given preset, if any
        :param preset: A given preset that describes the query type
        """
        if preset in self._NON_DEFAULT_FILTER_FUNCTION_MAPPINGS.keys():
            return self._NON_DEFAULT_FILTER_FUNCTION_MAPPINGS[preset].get(prop, None)

        if preset in self._DEFAULT_FILTER_FUNCTION_MAPPINGS.keys():
            if any(
                k in self._DEFAULT_FILTER_FUNCTION_MAPPINGS[preset] for k in ("*", prop)
            ):
                return self._get_default_filter_func(preset)

        raise QueryMappingError(
            """
            Error: failed to get filter_function mapping, the property is valid
            but does not contain an entry in DEFAULT_FILTER_FUNCTION_MAPPINGS
            or NON_DEFAULT_FILTER_FUNCTION_MAPPINGS. Please raise an issue with repo maintainer
        """
        )

    def _get_default_filter_func(
        self, preset: QueryPresets
    ) -> Optional[Callable[[Any], bool]]:
        """
        Returns a default filter function for preset, if any
        :param preset: preset to get default filter function for
        """
        return self._DEFAULT_FILTER_FUNCTIONS.get(preset, None)

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
            raise RuntimeError(
                """
                query ran but no properties selected use select() method to
                set properties or select_all() to select all available properties
            """
            )

        force_filter_func_usage = False
        with self._connection_cls(cloud_account) as conn:
            if "from_subset" in kwargs:
                self._results_resource_objects = self._parse_subset(
                    conn, kwargs["from_subset"]
                )
                force_filter_func_usage = True
            else:
                self._results_resource_objects = self._run_query(
                    conn, self._filter_kwargs, **kwargs
                )

        if self._filter_kwargs is None or force_filter_func_usage:
            self._results_resource_objects = self._apply_filter_func(
                self._results_resource_objects,
                self._filter_func,
            )

        self._results = self._parse_properties(
            self._results_resource_objects, self._query_props
        )

        return self

    @staticmethod
    def _parse_properties(
        items: List[Any],
        property_funcs: Dict[str, Callable[[Any], Any]],
    ) -> List[Dict[str, str]]:
        """
        Generates a dictionary of queried properties from a list of openstack objects e.g. servers
        :param items: List of items to obtain properties from
        :param property_funcs: property_functions that return properties requested
        :return: List containing dictionaries of the requested properties obtained from the items
        """
        return [QueryWrapper._parse_property(item, property_funcs) for item in items]

    @staticmethod
    def _parse_property(
        item: Any, property_funcs: Dict[str, Callable[[Any], Any]]
    ) -> Dict[str, str]:
        """
        Generates a dictionary of queried properties from a single openstack object
        :param item: openstack resource item to obtain properties from
        :param property_funcs: Dict of 'property_name' 'property_function' key value pairs
        """
        return {
            prop_key: QueryWrapper._run_prop_func(
                item, prop_func, default_out="Not Found"
            )
            for prop_key, prop_func in property_funcs.items()
        }

    @staticmethod
    def _run_prop_func(
        item: Any, prop_func: Callable[[Any], Any], default_out="Not Found"
    ) -> str:
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
    def _apply_filter_func(
        items: List[Any], query_func: Callable[[Any], bool]
    ) -> List[Any]:
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
    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> List[Any]:
        """
        This method is to be instantiated in subclasses of this class to run openstack query command
        """
        raise NotImplementedError(
            """
            This static method should be implemented in subclasses of QueryWrapper to
            run the appropriate openstack command(s)
        """
        )

    def to_list(self, as_objects=False) -> Union[List[Any], List[Dict[str, str]]]:
        """
        Public method to return results as a list
        :param as_objects: whether to return a list of openstack objects, or a list of dictionaries containing selected properties
        """
        return self._results_resource_objects if as_objects else self._results

    def to_string(self, **kwargs) -> str:
        """
        Public method to return results as a table
        :param kwargs: kwargs to pass to generate table
        """
        return self._generate_table(self._results, return_html=False, **kwargs)

    def to_html(self, **kwargs) -> str:
        """
        Public method to return results as html table
        :param kwargs: kwargs to pass to generate table
        """
        return self._generate_table(self._results, return_html=True, **kwargs)

    @staticmethod
    def _generate_table(
        properties_dict: List[Dict[str, Any]], return_html: bool, **kwargs
    ) -> str:
        """
        Returns a table from the result of 'self._parse_properties'
        :param properties_dict: dict of query results
        :param return_html: True if output required in html table format else output plain text table
        :param kwargs: kwargs to pass to tabulate
        :return: String (html or plaintext table of results)
        """
        headers = list(properties_dict[0].keys())
        rows = [list(row.values()) for row in properties_dict]
        return tabulate(
            rows, headers, tablefmt="html" if return_html else "grid", **kwargs
        )
