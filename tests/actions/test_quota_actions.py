from unittest.mock import create_autospec, NonCallableMock

from openstack_api.openstack_quota import OpenstackQuota
from src.quota_actions import QuotaActions
from structs.quota_details import QuotaDetails
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestQuotaActions(OpenstackActionTestBase):
    """
    Unit tests for the Quota.* actions
    """

    action_cls = QuotaActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Prepares the mock API and injects it into a new instance
        """
        super().setUp()
        self.network_mock = create_autospec(OpenstackQuota)
        self.action: QuotaActions = self.get_action_instance(api_mock=self.network_mock)

    def test_quota_set(self):
        """
        Tests setting a quota calls the correct API with the specified arguments
        """
        cloud, project = NonCallableMock(), NonCallableMock()
        floating_ips, security_group_rules = NonCallableMock(), NonCallableMock()

        returned = self.action.quota_set(
            cloud, project, floating_ips, security_group_rules
        )
        self.network_mock.set_quota.assert_called_once_with(
            cloud,
            QuotaDetails(
                project_identifier=project,
                num_floating_ips=floating_ips,
                num_security_group_rules=security_group_rules,
            ),
        )
        assert returned is True
