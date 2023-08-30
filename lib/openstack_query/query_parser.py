from typing import List, Dict, Tuple, Union, Optional, Callable
import logging
from collections import OrderedDict
from enums.query.props.prop_enum import PropEnum
from custom_types.openstack_query.aliases import OpenstackResourceObj, PropValue
from exceptions.parse_query_error import ParseQueryError

logger = logging.getLogger(__name__)


class QueryParser:
    """
    Helper class for taking query output and parsing it into a format which can then be outputted.
    Performs any sorting / grouping the user has specified
    """

    def __init__(self, prop_enum_cls: PropEnum):
        self._prop_enum_cls = prop_enum_cls
        self._sort_by = {}
        self._group_by = None
        self._group_mappings = {}

    @property
    def group_by_prop(self):
        return self._group_by

    def parse_sort_by(self, *sort_by: Tuple[PropEnum, bool]) -> None:
        """
        Public method used to configure sorting results
        :param sort_by: one or more tuples of property name to sort by and order
            - set order to True for descending, False for ascending
        """
        self._sort_by = {}
        for prop, order in sort_by:
            if prop not in self._prop_enum_cls:
                raise ParseQueryError(
                    f"Error: Given property to sort by: {prop.name} is not supported by query"
                )
            order_log_str = "DESC" if order else "ASC"
            logging.debug(
                "adding sorting params: %s, order: %s", prop.name, order_log_str
            )
            self._sort_by.update({prop: order})

        logging.debug(
            "sort params: %s",
            "\n\t".join(
                f"{prop}, order: {'DESC' if order else 'ASC'}"
                for prop, order in self._sort_by.items()
            ),
        )

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
        to select for that group
        :param include_missing: a flag which if set includes an extra grouping for values
        that don't fall into any group specified in group_ranges
        """
        if group_by not in self._prop_enum_cls:
            raise ParseQueryError(
                f"Error: Given property to group by: {group_by.name} is not supported by query"
            )
        self._group_by = group_by
        all_prop_list = set()

        if group_ranges:
            logger.debug("creating filter functions for specified group ranges")
            prop_func = self._prop_enum_cls.get_prop_func(group_by)
            for name, prop_list in group_ranges.items():
                group_vals = tuple(prop_list)
                self._group_mappings[name] = (
                    lambda obj, lst=group_vals: prop_func(obj) in lst
                )
                all_prop_list.update(prop_list)

            # if ungrouped group wanted - filter for all not in any range specified
            if include_missing:
                logger.debug("creating filter function for ungrouped group")
                self._group_mappings["ungrouped results"] = (
                    lambda obj: prop_func(obj) not in all_prop_list
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
            obj_list = self._run_sort(obj_list)

        if self._group_by:
            obj_list = self._run_group_by(obj_list)
        return obj_list

    def _run_sort(
        self,
        obj_list: List[OpenstackResourceObj],
    ) -> List[OpenstackResourceObj]:
        """
        method which sorts a list of openstack objects based on a dictionary of sort_by specs
        :param obj_list: A list of openstack objects to sort
            - descending - True, ascending - False
        """

        logger.debug("running multi-sort")
        sort_num = len(self._sort_by)
        for i, (sort_key, reverse) in enumerate(
            reversed(tuple(self._sort_by.items())), 1
        ):
            logger.debug("running sort %s / %s", i, sort_num)
            logger.debug("sorting by: %s, reverse=%s", sort_key, reverse)
            prop_func = self._prop_enum_cls.get_prop_func(sort_key)
            obj_list.sort(key=prop_func, reverse=reverse)
        return obj_list

    def _build_unique_val_groups(
        self,
        obj_list: List[OpenstackResourceObj],
    ) -> Dict[str, Callable[[OpenstackResourceObj], bool]]:
        """
        helper method to find all unique values for a given property in query results, and then,
        for each unique value, create a group mapping
        :param obj_list: A list of openstack objects to group
        """
        prop_func = self._prop_enum_cls.get_prop_func(self._group_by)
        # ordered dict to mimic ordered set
        # this is to preserve order we see unique values in - in case a sort has been done already
        unique_vals = OrderedDict({prop_func(obj): None for obj in obj_list})
        logger.debug(
            "unique values found %s - each will become a group",
            ",".join(f"{val}" for val in unique_vals),
        )

        group_mappings = {}

        # build groups
        for val in unique_vals.keys():
            group_key = f"{self._group_by.name} with value {val}"
            group_mappings[group_key] = (
                lambda obj, test_val=val: prop_func(obj) == test_val
            )

        return group_mappings

    def _run_group_by(
        self,
        obj_list: List[OpenstackResourceObj],
    ) -> Dict[str, List[OpenstackResourceObj]]:
        """
        helper method apply a set of group mappings onto a list of openstack objects. Returns a dictionary of grouped
        values where the key is the group name and value is a list of openstack objects that belong to that group
        :param obj_list: list of openstack objects to group
        """

        # if group mappings not specified - make a group for each unique value found for prop
        if not self._group_mappings:
            logger.info(
                "no group ranges specified - grouping by unique values of %s property",
                self._group_by.name,
            )
            self._group_mappings = self._build_unique_val_groups(obj_list)

        return {
            name: [item for item in obj_list if map_func(item)]
            for name, map_func in self._group_mappings.items()
        }
