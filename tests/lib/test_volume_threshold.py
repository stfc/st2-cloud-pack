from unittest.mock import MagicMock

from shell_api.disk_space import DiskSpace
from shell_api.volume_threshold import VolumeThreshold


def test_get_disk_space_root():
    mocked_shutil = MagicMock()
    mocked_shutil.disk_usage.return_value = (0, 1, 2)
    instance = VolumeThreshold(shutil_di=mocked_shutil)

    returned = instance.get_disk_space()
    assert isinstance(returned, DiskSpace), f"Found: {returned}"
    assert returned.total == 0
    assert returned.used == 1
    assert returned.free == 2


def test_get_list_of_disks():
    instance = VolumeThreshold()
    returned = instance.get_disk_list()

    assert isinstance(returned, list)
    assert all(isinstance(i, str) for i in returned)
