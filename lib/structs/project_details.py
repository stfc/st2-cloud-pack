from dataclasses import dataclass
from typing import Optional


# pylint: disable=too-many-instance-attributes
@dataclass
class ProjectDetails:
    name: str
    email: str
    description: str = ""
    project_domain: str = None
    is_enabled: Optional[bool] = None
    openstack_id: Optional[str] = None
    immutable: Optional[bool] = None
    parent_id: Optional[str] = None
