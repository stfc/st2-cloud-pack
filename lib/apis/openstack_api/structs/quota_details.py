from typing import Optional, Dict
from dataclasses import dataclass


# pylint: disable=too-many-instance-attributes
@dataclass
class QuotaDetails:
    project_identifier: str
    floating_ips: Optional[int] = None
    security_group_rules: Optional[int] = None
    cores: Optional[int] = None
    gigabytes: Optional[int] = None
    instances: Optional[int] = None
    backups: Optional[int] = None
    ram: Optional[int] = None
    security_groups: Optional[int] = None
    snapshots: Optional[int] = None
    volumes: Optional[int] = None

    def get_compute_quotas(self) -> Dict:
        """Return compute-related quotas that need to be set."""
        return {
            key: value
            for key, value in {
                "cores": self.cores,
                "ram": self.ram,
                "instances": self.instances,
            }.items()
            if value is not None
        }

    def get_network_quotas(self) -> Dict[str, int]:
        """Return network-related quotas that are not None."""
        return {
            key: value
            for key, value in {
                "floating_ips": self.floating_ips,
                "security_groups": self.security_groups,
                "security_group_rules": self.security_group_rules,
            }.items()
            if value is not None
        }

    def get_volume_quotas(self) -> Dict[str, int]:
        """Return volume-related quotas that are not None."""
        return {
            key: value
            for key, value in {
                "volumes": self.volumes,
                "snapshots": self.snapshots,
                "gigabytes": self.gigabytes,
                "backups": self.backups,
            }.items()
            if value is not None
        }

    def get_all_quotas(self) -> Dict[str, Dict[str, int]]:
        """Return all quotas grouped by service type."""
        return {
            "compute": self.get_compute_quotas(),
            "network": self.get_network_quotas(),
            "volume": self.get_volume_quotas(),
        }
