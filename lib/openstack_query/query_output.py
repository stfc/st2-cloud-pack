from typing import Any, List, Dict
from tabulate import tabulate

from enums.query.props.prop_enum import PropEnum
from exceptions.query_property_mapping_error import QueryPropertyMappingError
from openstack_query.handlers.prop_handler import PropHandler
from custom_types.openstack_query.aliases import OpenstackResourceObj


class QueryOutput:
    """
    Helper class for generating output for the query as a formatted table or selected properties - either as
    html or string

    TODO: Class should also handle grouping and sorting results
    """

    def __init__(self, prop_handler: PropHandler):
        self._prop_handler = prop_handler
        self._props = set()
        self._results = []

    @property
    def results(self) -> List[OpenstackResourceObj]:
        return self._results

    def sort_by(self, sort_by: PropEnum, reverse=False) -> List[OpenstackResourceObj]:
        """
        Public method used to configure sorting results
        :param sort_by: name of property to sort by
        :param reverse: False is sort by ascending, True is sort by descending, default False
        """
        raise NotImplementedError

    def group_by(self, group_by: PropEnum) -> List[Dict[str, OpenstackResourceObj]]:
        """
        Public method used to configure grouping results.
        :param group_by: name of the property to group by
        """
        raise NotImplementedError

    def to_string(self, **kwargs) -> str:
        """
        method to return results as a table
        :param kwargs: kwargs to pass to generate table
        """
        return self._generate_table(self._results, return_html=False, **kwargs)

    def to_html(self, **kwargs) -> str:
        """
        method to return results as html table
        :param kwargs: kwargs to pass to generate table
        """
        return self._generate_table(self._results, return_html=True, **kwargs)

    def parse_select(self, *props: PropEnum, select_all=False) -> None:
        """
        Method which is used to set which properties to output once results are gathered
        This method checks that each Enum provided is valid and populates internal attribute self._props
        :param select_all: boolean flag to select all valid properties
        :param props: any number of Enums representing properties to show
        """
        if select_all:
            self._props = set(self._prop_handler.all_props())
        else:
            for prop in props:
                self._check_prop_valid(prop)
                self._props.add(prop)

    def _check_prop_valid(self, prop: PropEnum):
        """
        method which checks if the given property is valid - i.e. has an associated function mapping in
        self.prop_handler which takes a openstack resource and returns the corresponding property for that object
        :param prop: An enum representing the desired property
        """
        if not self._prop_handler.check_supported(prop):
            raise QueryPropertyMappingError(
                "Error: failed to get property mapping, property is not supported by prop_handler"
            )

    def generate_output(
        self, openstack_resources: List[OpenstackResourceObj]
    ) -> List[Dict[str, str]]:
        """
        Generates a dictionary of queried properties from a list of openstack objects e.g. servers
        e.g. {['server_name': 'server1', 'server_id': 'server1_id'],
              ['server_name': 'server2', 'server_id': 'server2_id']} etc.
        (if we selected 'server_name' and 'server_id' as properties
        :param openstack_resources: List of openstack objects to obtain properties from - e.g. [Server1, Server2]
        :return: List containing dictionaries of the requested properties obtained from the items
        """
        self._results = [self._parse_property(item) for item in openstack_resources]
        return self._results

    def _parse_property(
        self, openstack_resource: OpenstackResourceObj
    ) -> Dict[str, str]:
        """
        Generates a dictionary of queried properties from a single openstack object
        :param openstack_resource: openstack resource item to obtain properties from
        """
        return {
            prop.name.lower(): self._prop_handler.get_prop(
                openstack_resource, prop, default_out="Not Found"
            )
            for prop in self._props
        }

    @staticmethod
    def _generate_table(
        results: List[Dict[str, Any]], return_html: bool, **kwargs
    ) -> str:
        """
        Returns a table from the result of 'self._parse_properties'
        :param results: dict of query results
        :param return_html: True if output required in html table format else output plain text table
        :param kwargs: kwargs to pass to tabulate
        :return: String (html or plaintext table of results)
        """
        if results:
            headers = list(results[0].keys())
            rows = [list(row.values()) for row in results]
            return tabulate(
                rows, headers, tablefmt="html" if return_html else "grid", **kwargs
            )
        return "No results found"
