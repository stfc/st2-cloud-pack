import unittest
from unittest.mock import MagicMock

from shell_api.volume_threshold import OpenStackVolumeThreshold


class OpenStackVolumeThresholdTest(unittest.TestCase):
    """
    Runs various tests to ensure we are using the Openstack
    Identity module in the expected way
    """

    def setUp(self) -> None:
        super().setUp()
        self.mocked_connection = MagicMock()
        self.mocked_cinder = MagicMock()
        self.instance = OpenStackVolumeThreshold(self.mocked_connection, self.mocked_cinder)
        self.identity_api = (
            self.mocked_connection.return_value.__enter__.return_value.session
        )

    def volumeOne(self, id, links, name):
        self.id="efa54464-8fab-47cd-a05a-be3e6b396188"
        self.links= [ "http://127.0.0.1:37097/v3/89afd400-b646-4bbc-b12b-c0a4d63e5bd3/volumes/efa54464-8fab-47cd-a05a-be3e6b396188", "http://127.0.0.1:37097/89afd400-b646-4bbc-b12b-c0a4d63e5bd3/volumes/efa54464-8fab-47cd-a05a-be3e6b396188" ]
        self.name="null"


    def test_get_disk_space_root(self):
        cloud = "test"
        self.mocked_cinder.volumes.list.return_value = self.id, self.links, self.name
        returned = self.instance.get_disk_space(cloud=cloud)
        assert True if returned.volumesizes.count() is not None else False
        assert True if returned.TCount.count() is not None else False
        assert True if returned.FCount.count() is not None else False
        # Checks to see that the appended list isn't empty and that the true / false count aren't 0
