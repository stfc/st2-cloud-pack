from typing import List, Dict, Union, Type, Set, Optional
from tabulate import tabulate

from enums.query.props.prop_enum import PropEnum
from exceptions.parse_query_error import ParseQueryError

from custom_types.openstack_query.aliases import OpenstackResourceObj, PropValue


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
        if not self._props:
            return []
        return list(self._props)

    @selected_props.setter
    def selected_props(self, props=Set[PropEnum]):
        self._props = props

    def to_string(
        self,
        results: Union[List, Dict],
        title: str = None,
        groups: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        method to return results as a table
        :param results: a list of parsed query results - either a list or a dict of grouped results
        :param title: a title for the table(s) when it gets outputted
        :param groups: a list group to limit output by
        :param kwargs: kwargs to pass to _generate_table method
        """
        output = ""
        if title:
            output += f"{title}:\n"

        if isinstance(results, dict):
            if groups and any(group not in results.keys() for group in groups):
                raise ParseQueryError(
                    f"given group(s) {groups} not found - available groups {list(results.keys())}"
                )

            if not groups:
                groups = list(results.keys())

            for group_title in groups:
                group_list = results[group_title]
                output += self._generate_table(
                    group_list, return_html=False, title=f"{group_title}:\n", **kwargs
                )
        elif groups:
            raise ParseQueryError(
                f"Result is not grouped - cannot filter by given group(s) {groups}"
            )

        else:
            output += self._generate_table(
                results, return_html=False, title=None, **kwargs
            )
        return output

    def to_html(
        self,
        results: Union[List, Dict],
        title: str = None,
        groups: Optional[List[str]] = None,
        **kwargs,
    ) -> str:
        """
        method to return results as html table
        :param results: a list of parsed query results - either a list or a dict of grouped results
        :param title: a title for the table(s) when it gets outputted
        :param groups: a list group to limit output by
        :param kwargs: kwargs to pass to generate table
        """
        output = ""
        if title:
            output += f"<b> {title} </b><br/> "

        if isinstance(results, dict):
            if groups and any(group not in results.keys() for group in groups):
                raise ParseQueryError(
                    f"given group(s) {groups} not found - available groups {list(results.keys())}"
                )

            if not groups:
                groups = list(results.keys())

            for group_title in groups:
                group_list = results[group_title]
                output += self._generate_table(
                    group_list,
                    return_html=True,
                    title=f"<b> {group_title}: </b><br/> ",
                    **kwargs,
                )
        elif groups:
            raise ParseQueryError(
                f"Result is not grouped - cannot filter by given group(s) {groups}"
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

        selected_props = set(self.selected_props)
        self.selected_props = selected_props.union(all_props)

    def generate_output(
        self, openstack_resources: List[OpenstackResourceObj]
    ) -> List[Dict[str, PropValue]]:
        """
        Generates a dictionary of queried properties from a list of openstack objects e.g. servers
        e.g. {['server_name': 'server1', 'server_id': 'server1_id'],
              ['server_name': 'server2', 'server_id': 'server2_id']} etc.
        (if we selected 'server_name' and 'server_id' as properties
        :param openstack_resources: List of openstack objects to obtain properties from - e.g. [Server1, Server2]
        :return: List containing dictionaries of the requested properties obtained from the items
        """
        return [self._parse_property(item) for item in openstack_resources]

    def _parse_property(
        self, openstack_resource: OpenstackResourceObj
    ) -> Dict[str, PropValue]:
        """
        Generates a dictionary of queried properties from a single openstack object
        :param openstack_resource: openstack resource item to obtain properties from
        """
        obj_dict = {}
        for prop in self.selected_props:
            prop_func = self._prop_enum_cls.get_prop_mapping(prop)
            try:
                val = str(prop_func(openstack_resource))
            except AttributeError:
                val = self.DEFAULT_OUT
            obj_dict[prop.name.lower()] = val
        return obj_dict

    @staticmethod
    def _generate_table(
        results: List[Dict[str, PropValue]], return_html: bool, title=None, **kwargs
    ) -> str:
        """
        Returns a table from the result of 'self._parse_properties'
        :param results: dict of query results
        :param return_html: True if output required in html table format else output plain text table
        :param kwargs: kwargs to pass to tabulate
        :return: String (html or plaintext table of results)
        """
        output = ""
        if title:
            output += f"{title}\n"

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
            vals = [d[key] for d in data]
            # converting into a set preserving order
            # https://stackoverflow.com/a/53657523
            vals = list(dict.fromkeys(vals))
            res[key] = vals
        return res
