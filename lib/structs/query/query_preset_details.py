from typing import Any, Dict
from enum import Enum
from dataclasses import dataclass

from enums.query.query_presets import QueryPresets


@dataclass
class QueryPresetDetails:
    """
    Structured data passed to a Query<Resource> object when calling the where() function
    describes how to filter for the query.
    """

    preset: QueryPresets
    prop: Enum
    args: Dict[str, Any]
