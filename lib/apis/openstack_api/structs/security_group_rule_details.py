from dataclasses import dataclass
from typing import Tuple

from apis.openstack_api.enums.ip_version import IPVersion
from apis.openstack_api.enums.network_direction import NetworkDirection
from apis.openstack_api.enums.protocol import Protocol


@dataclass
class SecurityGroupRuleDetails:
    security_group_identifier: str
    project_identifier: str

    direction: NetworkDirection
    ip_version: IPVersion
    protocol: Protocol
    remote_ip_cidr: str

    port_range: Tuple[str, str]
