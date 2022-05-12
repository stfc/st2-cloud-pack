from dataclasses import dataclass


@dataclass
class QuotaDetails:
    project_identifier: str

    num_floating_ips: int
    num_security_group_rules: int
