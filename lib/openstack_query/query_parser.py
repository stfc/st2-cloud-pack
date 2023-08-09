from typing import List, Dict, Tuple, Union, Optional, Set, Callable

from enums.query.props.prop_enum import PropEnum
from openstack_query.handlers.prop_handler import PropHandler
from custom_types.openstack_query.aliases import OpenstackResourceObj, PropValue

from exceptions.query_property_mapping_error import QueryPropertyMappingError
from exceptions.parse_query_error import ParseQueryError


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
        self._sort_by = set()
        for prop_name, order in sort_by:
            self._check_prop_valid(prop_name)
            order = order.upper()
            if order not in ["ASC", "DESC"]:
                raise ParseQueryError(
                    f"order specification given for sort-by '{order}' "
                    "is invalid, choose ASC (ascending) or DESC (descending)"
                )
            self._sort_by.add((prop_name, order == "DESC"))

    def parse_group_by(
        self,
        group_by: PropEnum,
        group_ranges: Optional[Dict[str, List[PropValue]]] = None,
        include_missing: Optional[bool] = False,
    ) -> None:
        """
        Public method used to configure grouping results.
        :param group_by: name of the property to group by
        :param group_ranges: a dictionary containing names of the group and list of prop values
        to select for for that group
        :param include_missing: a flag which if set includes an extra grouping for values
        that don't fall into any group specified in group_ranges
        """
        self._check_prop_valid(group_by)
        self._group_by = group_by
        all_prop_list = set()

        if group_ranges:
            for name, prop_list in group_ranges.items():
                group_vals = tuple(prop_list)
                self._group_mappings.update(
                    {
                        name: (
                            lambda obj, lst=group_vals: self._prop_handler.get_prop(
                                obj, group_by
                            )
                            in lst
                        )
                    }
                )
                all_prop_list.update(prop_list)

            # if ungrouped group wanted - filter for all not in any range specified
            if include_missing:
                self._group_mappings.update(
                    {
                        "ungrouped results": lambda obj: self._prop_handler.get_prop(
                            obj, group_by
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
        if not obj_list:
            return obj_list

        # we sort first - assuming sorting is commutative to grouping
        if self._sort_by:
            obj_list = self._run_sort(obj_list, self._sort_by)

        if self._group_by:
            # if group mappings not specified - make a group for each unique value found for prop
            if not self._group_mappings:
                self._group_mappings = self._build_unique_val_groups(
                    obj_list, group_by_prop=self._group_by
                )
            obj_list = self._run_group_by(obj_list, self._group_mappings)

        return obj_list

    def _run_sort(
        self,
        obj_list: List[OpenstackResourceObj],
        sort_by_specs: Set[Tuple[PropEnum, bool]],
    ) -> List[OpenstackResourceObj]:
        for sort_key, reverse in reversed(tuple(sort_by_specs)):
            obj_list.sort(
                key=lambda obj, sk=sort_key: self._prop_handler.get_prop(obj, sk),
                reverse=reverse,
            )
        return obj_list

    def _build_unique_val_groups(
        self,
        obj_list: List[OpenstackResourceObj],
        group_by_prop: PropEnum,
    ) -> Dict[str, Callable[[OpenstackResourceObj], bool]]:

        unique_vals = set(
            self._prop_handler.get_prop(obj, group_by_prop) for obj in obj_list
        )
        group_mappings = {}

        # build groups
        for val in unique_vals:
            group_mappings.update(
                {
                    f"{group_by_prop.name} with value {val}": lambda obj, test_val=val: self._prop_handler.get_prop(
                        obj, group_by_prop
                    )
                    == test_val
                }
            )

        return group_mappings

    @staticmethod
    def _run_group_by(
        obj_list: List[OpenstackResourceObj],
        group_mappings: Dict[str, Callable[[OpenstackResourceObj], bool]],
    ) -> Dict[str, List[OpenstackResourceObj]]:
        return {
            name: [item for item in obj_list if map_func(item)]
            for name, map_func in group_mappings.items()
        }
