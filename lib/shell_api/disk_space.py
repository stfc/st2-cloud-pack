from dataclasses import dataclass


@dataclass
class DiskSpace:
    used: int
    free: int
    total: int
