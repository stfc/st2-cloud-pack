from typing import List, Dict, Optional, Union
import logging
from collections import OrderedDict
from openstack_query.query_blocks.result import Result
from enums.query.props.prop_enum import PropEnum
from custom_types.openstack_query.aliases import GroupMappings, GroupRanges, PropValue
from exceptions.parse_query_error import ParseQueryError

logger = logging.getLogger(__name__)


class QueryGrouper:
    """
    Helper class for implementing grouping on query outputs
    """

    def __init__(self, prop_enum_cls):
        self._prop_enum_cls = prop_enum_cls
        self._group_by = None
        self._group_mappings = {}

    def _build_unique_val_groups(
        self,
        obj_list: List,
    ) -> GroupMappings:
        """
        helper method to find all unique values for a given property in query results, and then,
        for each unique value, create a group mapping
        :param obj_list: A list of openstack objects to build unique groups for
        """
        prop_func = self._prop_enum_cls.get_prop_mapping(self._group_by)
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
            group_key = val
            group_mappings[group_key] = (
                lambda obj, test_val=val: prop_func(obj) == test_val
            )
        return group_mappings

    def _add_include_missing_group(self, group_ranges: GroupRanges):
        """
        Helper method used to add an extra group for group_by which includes
        all resource values not already included in any defined mappings
        :param group_ranges: A set of predefined group ranges to check against
        """
        # if ungrouped group wanted - filter for all not in any range specified
        all_prop_list = set()
        for _, prop_list in group_ranges.items():
            all_prop_list.update(set(prop_list))

        prop_func = self._prop_enum_cls.get_prop_mapping(self._group_by)
        logger.debug("creating filter function for ungrouped group")
        self._group_mappings["ungrouped results"] = (
            lambda obj: prop_func(obj) not in all_prop_list
        )

    def _parse_group_ranges(self, group_ranges: Optional[Dict[str, List[PropValue]]]):
        """
        helper method for parsing group ranges
        :param group_ranges: a dictionary containing names of the group and list of prop values
        to select for that group
        """
        logger.debug("creating filter functions for specified group ranges")
        prop_func = self._prop_enum_cls.get_prop_mapping(self._group_by)
        for name, prop_list in group_ranges.items():
            group_vals = tuple(prop_list)
            self._group_mappings[name] = (
                lambda obj, lst=group_vals: prop_func(obj) in lst
            )

    def run_group_by(self, obj_list: List[Result]) -> Dict[str, List[Result]]:
        """
        method apply a set of group mappings onto a list of openstack objects. Returns a dictionary of grouped
        values where the key is the group name and value is a list of result objects that belong to that group
        :param obj_list: a list of Result objects containing query results to group by
        """

        # if group mappings not specified - make a group for each unique value found for prop
        if not self._group_mappings:
            logger.info(
                "no group ranges specified - grouping by unique values of %s property",
                self._group_by.name,
            )
            self._group_mappings = self._build_unique_val_groups(
                [item.as_object() for item in obj_list]
            )

        return {
            name: [item for item in obj_list if map_func(item.as_object())]
            for name, map_func in self._group_mappings.items()
        }

    def _parse_group_by_inputs(self, prop):
        """
        Converts list of select() 'prop' user inputs into Enums, any string aliases will be converted into Enums
        :param prop: property to group by
        """
        if isinstance(prop, str):
            prop = self._prop_enum_cls.from_string(prop)
        return prop

    def parse_group_by(
        self,
        group_by: Union[str, PropEnum],
        group_ranges: Optional[GroupRanges] = None,
        include_missing: Optional[bool] = False,
    ) -> None:
        """
        Public method used to configure grouping results.
        :param group_by: name of the property to group by
        :param group_ranges: a dictionary containing names of the group and list of prop values
        to select for that group
        :param include_missing: a flag which, if set, will include an extra grouping for values
        that don't fall into any group specified in group_ranges
        """
        group_by = self._parse_group_by_inputs(group_by)

        if group_by not in self._prop_enum_cls:
            raise ParseQueryError(
                f"Error: Given property to group by: {group_by.name} is not supported by query"
            )

        self._group_by = group_by
        self._group_mappings = {}
        if group_ranges:
            self._parse_group_ranges(group_ranges)

        if include_missing:
            self._add_include_missing_group(group_ranges)
