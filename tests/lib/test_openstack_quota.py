import unittest
from unittest.mock import MagicMock, patch, NonCallableMock, call

from openstack_api.openstack_quota import OpenstackQuota


class OpenstackQuotaTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the various mocks required in this test
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        with patch("openstack_api.openstack_quota.OpenstackIdentity") as identity_mock:
            self.instance = OpenstackQuota(self.mocked_connection)
            self.identity_module = identity_mock.return_value

        self.network_api = (
            self.mocked_connection.return_value.__enter__.return_value.network
        )

    def test_set_quota_floating_ips(self):
        """
        Tests that setting floating IPs update the quota correctly
        """
        cloud, details = NonCallableMock(), NonCallableMock()
        details.num_security_group_rules = 0

        self.instance.set_quota(cloud, details)
        self.mocked_connection.assert_called_once_with(cloud)
        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, details.project_identifier
        )
        self.network_api.update_quota.assert_called_once_with(
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            floating_ips=details.num_floating_ips,
        )

    def test_set_quota_security_group_rules(self):
        """
        Tests that setting security group rules update the quota correctly
        """
        cloud, details = NonCallableMock(), NonCallableMock()
        details.num_floating_ips = 0

        self.instance.set_quota(cloud, details)
        self.mocked_connection.assert_called_once_with(cloud)
        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, details.project_identifier
        )
        self.network_api.update_quota.assert_called_once_with(
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            security_group_rules=details.num_security_group_rules,
        )

    def test_set_quota_everything(self):
        """
        Tests that setting every supported quota in a single test
        """
        cloud, details = NonCallableMock(), NonCallableMock()

        self.instance.set_quota(cloud, details)

        expected_calls = [
            call(
                project_id=self.identity_module.find_mandatory_project.return_value.id,
                floating_ips=details.num_floating_ips,
            ),
            call(
                project_id=self.identity_module.find_mandatory_project.return_value.id,
                security_group_rules=details.num_security_group_rules,
            ),
        ]

        self.network_api.update_quota.assert_has_calls(expected_calls, any_order=True)
        assert self.network_api.update_quota.call_count == 2
