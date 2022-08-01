import shutil
from typing import Optional, List

from shell_api.disk_space import DiskSpace


class VolumeThreshold:
    def __init__(self, shutil_di: Optional = None):
        self.shutil = shutil_di if shutil_di else shutil

    def get_disk_space(self) -> DiskSpace:
        # TODO: GET RID OF HARD CODED ROOT
        returned = self.shutil.disk_usage("/")
        return DiskSpace(total=returned[0], used=returned[1], free=returned[2])

    def get_disk_list(self) -> List[str]:
        # TODO: Check disks are real
        return ["NotADisk"]
