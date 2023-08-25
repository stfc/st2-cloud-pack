from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enums.query.query_output_types import QueryOutputTypes
from enums.query.props.prop_enum import PropEnum
from custom_types.openstack_query.aliases import PropValue


@dataclass
class QueryOutputDetails:
    """
    Structured data to pass to Query<Resource> object.
    Needed for certain query output actions -
        - setting which properties to use for select()
        - how to output them to_html(), to_string() etc.
        - how to group/sort results

    :param properties_to_select: What properties to select of results when outputting
    (if result other than openstack objects is wanted)
    :param output_type:
    """

    properties_to_select: List[PropEnum]
    output_type: QueryOutputTypes = QueryOutputTypes.TO_STR
    group_by: Optional[PropEnum] = None

    # TODO include ability to set these in stackstorm
    group_ranges: Optional[Dict[str, List[PropValue]]] = None
    include_ungrouped_results: bool = False

    # TODO include ability to set the order in stackstorm
    sort_by: Optional[List[Tuple[PropEnum, str]]] = None

    @staticmethod
    def from_kwargs(
        prop_cls: PropEnum,
        properties_to_select: Optional[List[str]] = None,
        output_type: Optional[str] = None,
        group_by: Optional[str] = None,
        sort_by: Optional[List[str]] = None,
        **kwargs
    ):
        """
        method to parse and create this dataclass from kwargs
        :param prop_cls: a PropEnum class to get enum from for properties to select
        :param properties_to_select: an optional list of strings representing properties to select
        :param output_type: an optional string representing the way to output result
        :param group_by: an optional string representing a property to group results by
        :param sort_by: an optional set of tuples representing way which properties to sort results by
        :param kwargs: A set of kwargs to parse and use to set attributes to dataclass
        """

        # set the default for props to select as all available props
        output_details = {
            **{
                "properties_to_select": list(prop_cls),
            },
            **kwargs,
        }

        if properties_to_select:
            output_details["properties_to_select"] = [
                prop_cls.from_string(prop) for prop in properties_to_select
            ]

        if output_type:
            output_details["output_type"] = QueryOutputTypes.from_string(output_type)

        if group_by:
            output_details["group_by"] = prop_cls.from_string(group_by)

        if sort_by:
            # setting sort order to only be ascending for now
            output_details["sort_by"] = [
                (prop_cls.from_string(prop), False) for prop in sort_by
            ]

        return QueryOutputDetails(**output_details)
