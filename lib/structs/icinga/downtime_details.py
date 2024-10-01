from dataclasses import dataclass
from typing import Optional


@dataclass
class DowntimeDetails:
    object_type: str
    object_name: str
    start_time: int
    duration: int
    comment: str
    is_fixed: Optional[bool] = True
