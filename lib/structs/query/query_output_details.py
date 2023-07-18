from dataclasses import dataclass
from typing import Optional, List
from enums.query.query_output_types import QueryOutputTypes
from enums.query.props.prop_enum import PropEnum


@dataclass
class QueryOutputDetails:
    """
    Structured data to pass to Query<Resource> object. Needed for certain query output actions -
    setting which properties to select select(), or select_all(),
    and how to output them to_html(), to_string() etc.
    """

    properties_to_select: Optional[List[PropEnum]] = None
    output_type: Optional[QueryOutputTypes] = None

    @staticmethod
    def from_kwargs(prop_cls: PropEnum, **kwargs):
        """
        method to parse and create this dataclass from kwargs
        :param prop_cls a PropEnum class to get enum from for properties to select
        :param kwargs: A set of kwargs to parse and use to set attributes to dataclass
        """
        props = {prop_cls.from_string(prop) for prop in kwargs["properties_to_select"]}
        output_type = QueryOutputTypes.from_string(kwargs["output_type"])
        return QueryOutputDetails(
            properties_to_select=list(props), output_type=output_type
        )
