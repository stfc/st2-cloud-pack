from typing import List, Dict, Tuple, Union, Optional, Callable
import logging
from collections import OrderedDict
from enums.query.props.prop_enum import PropEnum
from openstack_query.handlers.prop_handler import PropHandler
from custom_types.openstack_query.aliases import OpenstackResourceObj, PropValue
from exceptions.query_property_mapping_error import QueryPropertyMappingError

logger = logging.getLogger(__name__)


class QueryParser:
    """
    Helper class for taking query output and parsing it into a format which can then be outputted.
    Performs any sorting / grouping the user has specified
    """

    def __init__(self, prop_handler: PropHandler):
        self._prop_handler = prop_handler
        self._sort_by = {}
        self._group_by = None
        self._group_mappings = {}

    @property
    def group_by_prop(self):
        return self._group_by

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

    def parse_sort_by(self, *sort_by: Tuple[PropEnum, bool]) -> None:
        """
        Public method used to configure sorting results
        :param sort_by: one or more tuples of property name to sort by and order
            - set order to True for descending, False for ascending
        """
        self._sort_by = {}
        for prop, order in sort_by:
            self._check_prop_valid(prop)
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
        self._check_prop_valid(group_by)
        self._group_by = group_by
        all_prop_list = set()

        if group_ranges:
            logger.debug("creating filter functions for specified group ranges")
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
                logger.debug("creating filter function for ungrouped group")
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
                logger.info(
                    "no group ranges specified - grouping by unique values of %s property",
                    self._group_by.name,
                )
                self._group_mappings = self._build_unique_val_groups(
                    obj_list, group_by_prop=self._group_by
                )
            obj_list = self._run_group_by(obj_list, self._group_mappings)

        return obj_list

    def _run_sort(
        self,
        obj_list: List[OpenstackResourceObj],
        sort_by_specs: Dict[PropEnum, bool],
    ) -> List[OpenstackResourceObj]:
        """
        method which sorts a list of openstack objects based on a dictionary of sort_by specs
        :param obj_list: A list of openstack objects to sort
        :param sort_by_specs: A dictionary of property to sort by as key and value as boolean representing order
            - descending - True, ascending - False
        """
        logger.debug("running multi-sort")
        sort_num = len(sort_by_specs)
        for i, (sort_key, reverse) in enumerate(
            reversed(tuple(sort_by_specs.items())), 1
        ):
            logger.debug("running sort %s / %s", i, sort_num)
            logger.debug("sorting by: %s, reverse=%s", sort_key, reverse)
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
        """
        helper method to find all unique values for a given property in query results, and then,
        for each unique value, create a group mapping
        :param obj_list: A list of openstack objects to group
        :param group_by_prop: A property enum to build unique-value group mappings for
        """

        # ordered dict to mimic ordered set
        # this is to preserve order we see unique values in - in case a sort has been done already
        unique_vals = OrderedDict(
            {self._prop_handler.get_prop(obj, group_by_prop): None for obj in obj_list}
        )
        logger.debug(
            "unique values found %s - each will become a group",
            ",".join(f"{val}" for val in unique_vals),
        )

        group_mappings = {}

        # build groups
        for val in unique_vals.keys():
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
        """
        helper method apply a set of group mappings onto a list of openstack objects. Returns a dictionary of grouped
        values where the key is the group name and value is a list of openstack objects that belong to that group
        :param obj_list: list of openstack objects to group
        :param group_mappings: a dictionary containing a group name as key and a group filter function as a value.
        """
        return {
            name: [item for item in obj_list if map_func(item)]
            for name, map_func in group_mappings.items()
        }
