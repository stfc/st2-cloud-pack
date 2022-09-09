import unittest
from unittest.mock import MagicMock

from openstack_api.openstack_hypervisor import OpenstackHypervisor


class OpenstackHypervisorTests(unittest.TestCase):
    """
    Runs various tests to ensure we are using the Openstack
    Hypervisor module works correctly
    """

    def setUp(self) -> None:
        super().setUp()
        self.mocked_connection = MagicMock()

        self.instance = OpenstackHypervisor(self.mocked_connection)
        self.api = self.mocked_connection.return_value.__enter__.return_value

        self.mock_hv_list = [
            {
                "id": "hypervisorid1",
                "name": "hv123",
                "state": "up",
                "status": "enabled",
                "vcpus_used": 2,
                "vcpus": 128,
                "memory_mb_used": 4096,
                "memory_mb": 515530,
            },
            {
                "id": "hypervisorid2",
                "name": "hv124",
                "state": "up",
                "status": "disabled",
                "vcpus_used": 2,
                "vcpus": 128,
                "memory_mb_used": 4096,
                "memory_mb": 515530,
            },
            {
                "id": "hypervisorid3",
                "name": "hv225",
                "state": "down",
                "status": "enabled",
                "vcpus_used": 2,
                "vcpus": 128,
                "memory_mb_used": 4096,
                "memory_mb": 515530,
            },
        ]

    def test_search_all_hvs(self):
        """
        Tests calling search_all_hvs
        """
        self.instance.search_all_hvs(cloud_account="test")

        self.mocked_connection.assert_called_once_with("test")

        self.api.list_hypervisors.assert_called_once_with(
            filters={},
        )

    def test_search_hvs_name_in(self):
        """
        Tests calling search_hvs_name_in
        """

        self.instance.search_all_hvs = MagicMock()
        self.instance.search_all_hvs.return_value = self.mock_hv_list

        result = self.instance.search_hvs_name_in(
            cloud_account="test",
            names=["hv123", "hv124"],
        )

        self.assertEqual(result, [self.mock_hv_list[0], self.mock_hv_list[1]])

    def test_search_hvs_name_not_in(self):
        """
        Tests calling search_hvs_name_not_in
        """

        self.instance.search_all_hvs = MagicMock()
        self.instance.search_all_hvs.return_value = self.mock_hv_list

        result = self.instance.search_hvs_name_not_in(
            cloud_account="test",
            names=["hv123", "hv124"],
        )

        self.assertEqual(result, [self.mock_hv_list[2]])

    def test_search_hvs_name_contains(self):
        """
        Tests calling search_hvs_name_contains
        """

        self.instance.search_all_hvs = MagicMock()
        self.instance.search_all_hvs.return_value = self.mock_hv_list

        result = self.instance.search_hvs_name_contains(
            cloud_account="test",
            name_snippets=["hv", "12"],
        )

        self.assertEqual(result, [self.mock_hv_list[0], self.mock_hv_list[1]])

        result = self.instance.search_hvs_name_contains(
            cloud_account="test", name_snippets=["hv22"]
        )

        self.assertEqual(result, [self.mock_hv_list[2]])

        result = self.instance.search_hvs_name_contains(
            cloud_account="test", name_snippets=["hv"]
        )

        self.assertEqual(result, self.mock_hv_list)

    def test_search_hvs_name_not_contains(self):
        """
        Tests calling search_hvs_name_not_contains
        """

        self.instance.search_all_hvs = MagicMock()
        self.instance.search_all_hvs.return_value = self.mock_hv_list

        result = self.instance.search_hvs_name_not_contains(
            cloud_account="test",
            name_snippets=["hv", "12"],
        )

        self.assertEqual(result, [])

        result = self.instance.search_hvs_name_not_contains(
            cloud_account="test", name_snippets=["hv22"]
        )

        self.assertEqual(result, [self.mock_hv_list[0], self.mock_hv_list[1]])

        result = self.instance.search_hvs_name_not_contains(
            cloud_account="test", name_snippets=["hv"]
        )

        self.assertEqual(result, [])

    def test_search_hv_id_in(self):
        """
        Tests calling search_hvs_id_in
        """

        self.instance.search_all_hvs = MagicMock()
        self.instance.search_all_hvs.return_value = self.mock_hv_list

        result = self.instance.search_hvs_id_in(
            cloud_account="test", ids=["hypervisorid1", "hypervisorid2"]
        )

        self.assertEqual(result, [self.mock_hv_list[0], self.mock_hv_list[1]])

    def test_search_hvs_id_not_in(self):
        """
        Tests calling search_hvs_id_not_in
        """

        self.instance.search_all_hvs = MagicMock()
        self.instance.search_all_hvs.return_value = self.mock_hv_list

        result = self.instance.search_hvs_id_not_in(
            cloud_account="test", ids=["hypervisorid1", "hypervisorid2"]
        )

        self.assertEqual(result, [self.mock_hv_list[2]])

    def test_search_hv_down(self):
        """
        Tests calling search_hvs_down
        """

        self.instance.search_all_hvs = MagicMock()
        self.instance.search_all_hvs.return_value = self.mock_hv_list

        result = self.instance.search_hvs_down(cloud_account="test")

        self.assertEqual(result, [self.mock_hv_list[2]])

    def test_search_hv_up(self):
        """
        Tests calling search_hvs_up
        """

        self.instance.search_all_hvs = MagicMock()
        self.instance.search_all_hvs.return_value = self.mock_hv_list

        result = self.instance.search_hvs_up(cloud_account="test")

        self.assertEqual(result, [self.mock_hv_list[0], self.mock_hv_list[1]])

    def test_search_hv_disabled(self):
        """
        Tests calling search_hvs_disabled
        """

        self.instance.search_all_hvs = MagicMock()
        self.instance.search_all_hvs.return_value = self.mock_hv_list

        result = self.instance.search_hvs_disabled(cloud_account="test")

        self.assertEqual(result, [self.mock_hv_list[1]])

    def test_search_hv_enabled(self):
        """
        Tests calling search_hvs_enabled
        """

        self.instance.search_all_hvs = MagicMock()
        self.instance.search_all_hvs.return_value = self.mock_hv_list

        result = self.instance.search_hvs_enabled(cloud_account="test")

        self.assertEqual(result, [self.mock_hv_list[0], self.mock_hv_list[2]])
