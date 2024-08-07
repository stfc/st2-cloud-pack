from unittest.mock import create_autospec, NonCallableMock, NonCallableMagicMock

from enums.ip_version import IPVersion
from enums.network_direction import NetworkDirection
from enums.protocol import Protocol
from openstack_api.openstack_security_groups import OpenstackSecurityGroups
from src.security_group_actions import SecurityGroupActions
from structs.security_group_rule_details import SecurityGroupRuleDetails
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestNetworkActions(OpenstackActionTestBase):
    """
    Unit tests for the SecurityGroup.* actions
    """

    action_cls = SecurityGroupActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Initialises the action and injects mocks required for testing
        """
        super().setUp()
        self.security_group_mock = create_autospec(OpenstackSecurityGroups)
        self.action: SecurityGroupActions = self.get_action_instance(
            api_mocks=self.security_group_mock
        )

    def test_create_security_group_success(self):
        """
        Tests create security group forwards the new security group if successful
        """
        args = [NonCallableMock() for _ in range(4)]
        result = self.action.security_group_create(*args)
        self.security_group_mock.create_security_group.assert_called_once_with(*args)
        expected = self.security_group_mock.create_security_group.return_value
        assert result == (True, expected)

    def test_create_security_group_failure(self):
        """
        Tests method returns status and error string on failure
        """
        self.security_group_mock.create_security_group.return_value = None
        result = self.action.security_group_create(
            *(NonCallableMock() for _ in range(4))
        )
        assert result == (False, None)

    def test_create_security_group_rule_success(self):
        """
        Tests method forwards the new security group rule if successful
        """
        cloud = NonCallableMock()
        mocked_details = SecurityGroupRuleDetails(
            *(NonCallableMagicMock() for _ in range(7))
        )

        # Since these will be deserialised we need to have real values
        mocked_details.direction = NetworkDirection.INGRESS
        mocked_details.ip_version = IPVersion.IPV4
        mocked_details.protocol = Protocol.TCP

        result = self.action.security_group_rule_create(
            cloud_account=cloud,
            project_identifier=mocked_details.project_identifier,
            security_group_identifier=mocked_details.security_group_identifier,
            # Convert to lower to check case handling
            direction=mocked_details.direction.value.lower(),
            ether_type=mocked_details.ip_version.value.lower(),
            protocol=mocked_details.protocol.value.lower(),
            remote_ip_prefix=mocked_details.remote_ip_cidr,
            start_port=mocked_details.port_range[0],
            end_port=mocked_details.port_range[1],
        )

        expected = self.security_group_mock.create_security_group_rule.return_value
        assert result == (True, expected)

    def test_create_security_group_rule_failure(self):
        """
        Tests method returns status and error string on failure
        """
        self.security_group_mock.create_security_group_rule.return_value = None
        result = self.action.security_group_rule_create(
            cloud_account=NonCallableMock(),
            project_identifier=NonCallableMock(),
            security_group_identifier=NonCallableMock(),
            # Convert to lower to check case handling
            direction=NetworkDirection.INGRESS.value.lower(),
            ether_type=IPVersion.IPV4.value.lower(),
            protocol=Protocol.TCP.value.lower(),
            remote_ip_prefix=NonCallableMock(),
            start_port=NonCallableMock(),
            end_port=NonCallableMock(),
        )
        assert result == (False, None)

    def test_run_dispatches_correctly(self):
        """
        Tests that run finds the expected methods in this class
        """
        expected_methods = [
            "security_group_create",
            "security_group_rule_create",
            "security_group_list",
        ]
        self._test_run_dynamic_dispatch(expected_methods)

    def test_security_group_rule_set_external(self):
        """
        Tests that security_group_rule_set_external calls appropriate method
        """
        cloud, project_identifier, security_group_identifier = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )

        result = self.action.security_group_rule_set_external(
            cloud_account=cloud,
            project_identifier=project_identifier,
            security_group_identifier=security_group_identifier,
        )

        expected = (
            self.security_group_mock.create_external_security_group_rules.return_value
        )
        assert result == (True, expected)
