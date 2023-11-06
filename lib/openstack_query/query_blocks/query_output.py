from typing import List, Dict, Union, Type, Set, Optional, Tuple
from tabulate import tabulate
from enums.query.props.prop_enum import PropEnum
from custom_types.openstack_query.aliases import (
    OpenstackResourceObj,
    PropValue,
)
from exceptions.parse_query_error import ParseQueryError
from openstack_query.query_blocks.results_container import ResultsContainer


class QueryOutput:
    """
    Helper class for generating output for the query as a formatted table or selected properties - either as
    html or string

    TODO: Class should also handle grouping and sorting results
    """

    # what value to output if property is not found for an openstack object
    DEFAULT_OUT = "Not Found"

    def __init__(self, prop_enum_cls: Type[PropEnum]):
        self._prop_enum_cls = prop_enum_cls
        self._props = set()

    @property
    def selected_props(self) -> List[PropEnum]:
        """
        A getter for selected properties relevant to the query
        """
        if not self._props:
            return []
        return list(self._props)

    @selected_props.setter
    def selected_props(self, props=Set[PropEnum]):
        """
        A setter for setting selected properties
        :param props: A set of property enums to select for
        """
        self._props = props

    @staticmethod
    def _validate_groups(
        results: Union[List, Dict], groups: Optional[List[str]] = None
    ):

        if not groups:
            return results

        if not isinstance(results, dict):
            raise ParseQueryError(
                f"Result is not grouped - cannot filter by given group(s) {groups}"
            )
        if not all(group in results.keys() for group in groups):
            raise ParseQueryError(
                f"Group(s) given are invalid - valid groups {list(results.keys())}"
            )
        return {group_key: results[group_key] for group_key in groups}

    def to_objects(
        self, results_container: ResultsContainer, groups: Optional[List[str]] = None
    ) -> Union[Dict[str, List], List]:
        """
        return results as openstack objects
        :param results_container: container object which stores results
        :param groups: a list of group keys to limit output by

        """
        results = results_container.to_objects()
        return self._validate_groups(results, groups)

    def to_props(
        self,
        results_container: ResultsContainer,
        flatten: bool = False,
        groups: Optional[List[str]] = None,
    ) -> Union[Dict[str, List], List]:
        """
        return results as selected props
        :param results_container: container object which stores results
        :param flatten: boolean which will flatten results if true
        :param groups: a list of group keys to limit output by
        """
        results = results_container.to_props(*self.selected_props)
        results = self._validate_groups(results, groups)
        if flatten:
            results = self.flatten(results)
        return results

    def to_string(
        self,
        results_container: ResultsContainer,
        title: str = None,
        groups: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        return results as a table of selected properties
        :param results_container: container object which stores results
        :param title: an optional title for the table when it gets outputted
        :param groups: a list of groups to limit output by
        :param kwargs: kwargs to pass to _generate_table method
        """
        results = results_container.to_props(*self.selected_props)
        results = self._validate_groups(results, groups)

        output = "" if not title else f"{title}:\n"

        if isinstance(results, dict):
            for group_title in list(results.keys()):
                output += self._generate_table(
                    results[group_title],
                    return_html=False,
                    title=f"{group_title}:\n",
                    **kwargs,
                )
        else:
            output += self._generate_table(
                results, return_html=False, title=None, **kwargs
            )
        return output

    def to_html(
        self,
        results_container: ResultsContainer,
        title: str = None,
        groups: Optional[List[str]] = None,
        **kwargs,
    ) -> str:
        """
        method to return results as html table
        :param results_container: container object which stores results
        :param title: a title for the table(s) when it gets outputted
        :param groups: a list of groups to limit output by
        :param kwargs: kwargs to pass to generate table
        """
        results = results_container.to_props(*self.selected_props)
        results = self._validate_groups(results, groups)
        output = "" if not title else f"{title}:\n"

        if isinstance(results, dict):
            for group_title in list(results.keys()):
                output += self._generate_table(
                    results[group_title],
                    return_html=True,
                    title=f"<b> {group_title}: </b><br/> ",
                    **kwargs,
                )
        else:
            output += self._generate_table(
                results, return_html=True, title=None, **kwargs
            )
        return output

    def parse_select(self, *props: PropEnum, select_all=False) -> None:
        """
        Method which is used to set which properties to output once results are gathered
        This method checks that each Enum provided is valid and populates internal attribute which holds selected props
        :param select_all: boolean flag to select all valid properties
        :param props: any number of Enums representing properties to show
        """
        if select_all:
            self.selected_props = set(self._prop_enum_cls)
            return

        all_props = set()
        for prop in props:
            if prop not in self._prop_enum_cls:
                raise ParseQueryError(
                    f"Error: Given property to select: {prop.name} is not supported by query"
                )
            all_props.add(prop)

        self.selected_props = set(all_props)

    @staticmethod
    def _generate_table(
        results: List[Dict[str, PropValue]], return_html: bool, title=None, **kwargs
    ) -> str:
        """
        Returns a table from the result of 'self.parse_properties'
        :param results: dict of query results
        :param return_html: True if output required in html table format else output plain text table
        :param kwargs: kwargs to pass to tabulate
        :return: String (html or plaintext table of results)
        """
        output = "" if not title else f"{title}:\n"

        if results:
            headers = list(results[0].keys())
            rows = [list(row.values()) for row in results]
            output += tabulate(
                rows, headers, tablefmt="html" if return_html else "grid", **kwargs
            )
            output += "\n\n"
        else:
            output += "No results found"
        return output

    @staticmethod
    def flatten(data: Union[List, Dict]) -> Optional[Dict]:
        """
        Utility function for flattening output to instead get list of unique
        values found for each property selected. results will also be grouped if given
        data is grouped too
        :param data: output to flatten
        """
        if not data:
            return None

        if isinstance(data, list):
            return QueryOutput._flatten_list(data)

        result = {}
        for group_key, values in data.items():
            result[group_key] = QueryOutput._flatten_list(values)

        return result

    @staticmethod
    def _flatten_list(data: List[Dict]) -> Dict:
        """
        Helper function to flatten a query output list. This will return
        a dictionary where the keys are strings representing the property and
        the value is a list of unique values found in the given output list for that property.
        Output list can be actual query output (if it's a list) or one group of grouped results
        :param data: output list to flatten
        """
        if not data:
            return {}

        keys = list(data[0].keys())
        res = {}
        for key in keys:
            res[key] = [d[key] for d in data]
        return res
