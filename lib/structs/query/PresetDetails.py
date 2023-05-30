from dataclasses import dataclass
from enum import Enum

from enums.query.query_presets import QueryPresets
from typing import Any, Dict


@dataclass
class PresetDetails:
    """
    Structured data passed to a Query<Resource> object - describes how to filter for the query.
    One or more are needed when calling the where() function.
    """

    preset: QueryPresets
    prop: Enum
    args: Dict[str, Any]
