from typing import List, Dict, Tuple, Union

from enums.query.props.prop_enum import PropEnum
from exceptions.query_property_mapping_error import QueryPropertyMappingError
from openstack_query.handlers.prop_handler import PropHandler
from custom_types.openstack_query.aliases import OpenstackResourceObj, PropValue

from lib.exceptions.parse_query_error import ParseQueryError


class QueryParser:
    """
    Helper class for taking query output and parsing it into a format which can then be outputted.
    Performs any sorting / grouping the user has specified
    """

    def __init__(self, prop_handler: PropHandler):
        self._prop_handler = prop_handler
        self._sort_by = set()
        self._group_by = None
        self._group_mappings = {}

    def _check_prop_valid(self, prop: PropEnum) -> None:
        """
        method which checks if the given property is valid - i.e. has an associated function mapping in
        self.prop_handler which takes a openstack resource and returns the corresponding property for that object
        :param prop: An enum representing the desired property
        """
        if not self._prop_handler.check_supported(prop):
            raise QueryPropertyMappingError(
                "Error: failed to get property mapping, property is not supported by prop_handler"
            )

    def parse_sort_by(self, *sort_by: Tuple[PropEnum, str]) -> None:
        """
        Public method used to configure sorting results
        :param sort_by: tuples of property name to sort by and order "asc or desc"
        """
        for prop_name, order in sort_by:
            self._check_prop_valid(sort_by)
            if order.upper() not in ["ASC", "DESC"]:
                raise ParseQueryError(
                    f"order specification given for sort-by '{order}' "
                    "is invalid, choose ASC (ascending) or DESC (descending)"
                )
            self._sort_by.add((sort_by, True if order == "ASC" else False))

    def parse_group_by(
        self,
        group_by: PropEnum,
        group_ranges: Dict[str, List[PropValue]],
        include_ungrouped_results: bool,
    ) -> None:
        """
        Public method used to configure grouping results.
        :param group_by: name of the property to group by
        :param group_ranges: a dictionary containing names of the group and list of prop values
        to select for for that group
        :param include_ungrouped_results: a flag which if set includes an extra grouping for values
        that don't fall into any group specified in group_ranges
        """
        self._check_prop_valid(group_by)
        all_prop_list = set()
        for name, prop_list in group_ranges.items():
            self._group_mappings.update(
                {name: lambda obj: self._prop_handler.get_prop(group_by) in prop_list}
            )
            all_prop_list.update(prop_list)

        # if ungrouped group wanted - filter for all not in any range specified
        if include_ungrouped_results:
            self._group_mappings.update(
                {
                    "ungrouped results": lambda obj: self._prop_handler.get_prop(
                        group_by
                    )
                    not in all_prop_list
                }
            )

    def run_parser(
        self, obj_list: List[OpenstackResourceObj]
    ) -> Union[List[OpenstackResourceObj], Dict[str, List[OpenstackResourceObj]]]:
        """
        Public method used to parse query runner output - performs specified sorting and grouping
        :param obj_list: a list of openstack resource objects to parse
        """
        parsed_obj_list = obj_list
        if self._sort_by:

            def sort_function(item):
                return [
                    item[key] if order else -item[key] for key, order in self._sort_by
                ]

            parsed_obj_list = sorted(parsed_obj_list, key=sort_function)

        if self._group_by:
            parsed_obj_list = {
                name: [item for item in obj_list if map_func(item)]
                for name, map_func in self._group_mappings.items()
            }
        return parsed_obj_list
