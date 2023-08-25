import unittest
from dataclasses import dataclass
from unittest.mock import MagicMock


from openstack_api.openstack_hypervisor import OpenstackHypervisor

from tests.lib.test_openstack_query_base import OpenstackQueryBaseTests


@dataclass
class _HypervisorMock:
    vcpus_used: int = 4
    vcpus: int = 16
    memory_mb_used: int = 4096
    memory_mb: int = 16384
    local_gb_used: int = 10
    local_gb: int = 80

    def __getitem__(self, attr):
        return getattr(self, attr)


class OpenstackHypervisorTests(unittest.TestCase, OpenstackQueryBaseTests):
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

    def test_property_funcs(self):
        """
        Tests calling get_query_property_funcs
        """
        item = _HypervisorMock()
        property_funcs = self.instance.get_query_property_funcs("test")

        # Test vcpu_usage
        result = property_funcs["vcpu_usage"](item)
        self.assertEqual(result, f"{item.vcpus_used}/{item.vcpus}")

        # Test memory_mb_usage
        result = property_funcs["memory_mb_usage"](item)
        self.assertEqual(result, f"{item.memory_mb_used}/{item.memory_mb}")

        # Test local_gb_usage
        result = property_funcs["local_gb_usage"](item)
        self.assertEqual(result, f"{item.local_gb_used}/{item.local_gb}")

    def test_property_func_uptime_raises(self):
        """
        Tests the 'uptime' function returned by get_query_property_funcs raises
        """
        item = _HypervisorMock()
        with self.assertRaises(NotImplementedError):
            self.instance.get_query_property_funcs("test")["uptime"](item)

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
