from dataclasses import dataclass
from typing import Optional


@dataclass
class ProjectDetails:
    name: str
    email: str
    description: str = ""
    is_enabled: Optional[bool] = None
    openstack_id: Optional[str] = None
