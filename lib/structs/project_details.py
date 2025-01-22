from dataclasses import dataclass
from typing import Optional


@dataclass
class ProjectDetails:
    name: str
    email: str
    description: str = ""
    domain_id: Optional[str] = None
    is_enabled: Optional[bool] = None
    openstack_id: Optional[str] = None
    immutable: Optional[bool] = None
    parent_id: Optional[str] = None
