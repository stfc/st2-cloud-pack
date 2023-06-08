from enum import Enum
from dataclasses import dataclass
from typing import Optional, Set
from enums.query.query_output_types import QueryOutputTypes


@dataclass
class QueryDetails:
    properties_to_select: Optional[Set[Enum]]
    group_by: Optional[Enum]
    sort_by: Optional[Enum]
    output_type: Optional[QueryOutputTypes]
    # TODO define some meta openstacksdk args that can be passed into _run_query() as **kwargs
