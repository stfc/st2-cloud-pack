from dataclasses import dataclass
from typing import Optional

from apis.icinga_api.enums.icinga_objects import IcingaObject


@dataclass
class DowntimeDetails:
    object_type: IcingaObject
    object_name: str
    start_time: int
    end_time: int
    duration: int
    comment: str
    is_fixed: Optional[bool] = True
