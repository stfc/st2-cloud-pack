from dataclasses import dataclass
from typing import Optional

from apis.openstack_api.enums.rbac_network_actions import RbacNetworkActions


@dataclass
class NetworkRbac:
    project_identifier: str
    network_identifier: str
    name: Optional[str] = None
    action: Optional[RbacNetworkActions] = None
