from dataclasses import dataclass
from enum import Enum

from enums.query.query_presets import QueryPresets
from typing import Any, Dict


@dataclass
class QueryPresetDetails:
    """
    Structured data passed to a Query<Resource> object when calling the where() function
    describes how to filter for the query.
    """

    preset: QueryPresets
    prop: Enum
    args: Dict[str, Any]
