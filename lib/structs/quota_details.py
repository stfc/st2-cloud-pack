from dataclasses import dataclass


# pylint: disable=too-many-instance-attributes
@dataclass
class QuotaDetails:
    project_identifier: str
    floating_ips: int
    security_group_rules: int
    cores: int
    gigabytes: int
    instances: int
    backups: int
    ram: int
    security_groups: int
    snapshots: int
    volumes: int
    volumes: int
