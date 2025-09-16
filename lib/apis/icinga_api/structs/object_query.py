from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class IcingaQuery:
    """
    Dataclass containing filters and properties to return for icinga objects
    """

    object_type: str
    filter: str
    filter_vars: Dict
    properties_to_select: List[str]
    joins: Optional[List[str]] = None
