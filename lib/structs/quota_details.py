from dataclasses import dataclass


@dataclass
class QuotaDetails:
    project_identifier: str

    floating_ips: int
    secgroup_rules: int
    cores: int
    gigabytes: int
    instances: int
    backups: int
    ram: int
    secgroups: int
    snapshots: int
    volumes: int
