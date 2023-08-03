from dataclasses import dataclass
from typing import List
from enums.query.query_output_types import QueryOutputTypes
from enums.query.props.prop_enum import PropEnum


@dataclass
class QueryOutputDetails:
    """
    Structured data to pass to Query<Resource> object. Needed for certain query output actions -
    setting which properties to select select(), or select_all(),
    and how to output them to_html(), to_string() etc.
    """

    properties_to_select: List[PropEnum]
    output_type: QueryOutputTypes

    @staticmethod
    def from_kwargs(prop_cls: PropEnum, **kwargs):
        """
        method to parse and create this dataclass from kwargs
        :param prop_cls a PropEnum class to get enum from for properties to select
        :param kwargs: A set of kwargs to parse and use to set attributes to dataclass
        """
        props = list(prop_cls)
        output_type = QueryOutputTypes.TO_STR
        if "properties_to_select" in kwargs and kwargs["properties_to_select"]:
            props = [
                prop_cls.from_string(prop) for prop in kwargs["properties_to_select"]
            ]

        if "output_type" in kwargs and kwargs["output_type"]:
            output_type = QueryOutputTypes.from_string(kwargs["output_type"])
        return QueryOutputDetails(properties_to_select=props, output_type=output_type)
