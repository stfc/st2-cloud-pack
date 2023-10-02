from typing import Any, Dict
from enums.query.props.prop_enum import PropEnum
from dataclasses import dataclass

from enums.query.query_presets import QueryPresets


@dataclass
class QueryPresetDetails:
    """
    Structured data passed to a Query<Resource> object when calling the where() function
    describes how to filter for the query.
    """

    preset: QueryPresets
    prop: PropEnum
    args: Dict[str, Any]
