from enum import Enum
from dataclasses import dataclass
from typing import Optional, Set
from enums.query.query_output_types import QueryOutputTypes


@dataclass
class QueryOutputDetails:
    """
    Structured data to pass to Query<Resource> object. Needed for certain query output actions -
    setting which properties to select select(), or select_all(),
    and how to output them to_html(), to_string() etc.
    """

    properties_to_select: Optional[Set[Enum]] = None
    output_type: Optional[QueryOutputTypes] = None
