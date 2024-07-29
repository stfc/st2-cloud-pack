import unittest
from unittest.mock import (
    MagicMock,
    NonCallableMock,
    Mock,
    NonCallableMagicMock,
    patch,
    ANY,
)

from nose.tools import assert_raises, raises
from parameterized import parameterized

from enums.ip_version import IPVersion
from enums.network_direction import NetworkDirection
from enums.protocol import Protocol
from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_security_groups import OpenstackSecurityGroups
from structs.security_group_rule_details import SecurityGroupRuleDetails


class OpenstackSecurityGroupsTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the various mocks required in this test
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        with patch(
            "openstack_api.openstack_security_groups.OpenstackIdentity"
        ) as identity_mock:
            self.instance = OpenstackSecurityGroups(self.mocked_connection)
            self.identity_module = identity_mock.return_value

        self.network_api = (
            self.mocked_connection.return_value.__enter__.return_value.network
        )

    @raises(MissingMandatoryParamError)
    def test_find_security_group_raises_for_missing_identifier(self):
        """
        Tests that find security group raises if no identifier is provided
        """
        self.instance.find_security_group(
            NonCallableMock(),
            project_identifier=NonCallableMock(),
            security_group_identifier=" \t",
        )

    def test_find_security_group_forwards_result(self):
        """
        Tests find security group forwards found result
        """
        cloud, project, security_group = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        return_val = self.instance.find_security_group(cloud, project, security_group)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, project
        )
        self.mocked_connection.assert_called_with(cloud)
        self.network_api.find_security_group.assert_called_once_with(
            security_group.strip(),
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            ignore_missing=True,
        )
        assert return_val == self.network_api.find_security_group.return_value

    def test_search_security_groups(self):
        """
        Tests search security group returns the expected list
        """
        cloud, project = NonCallableMock(), NonCallableMock()
        return_val = self.instance.search_security_group(cloud, project)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, project_identifier=project
        )
        found_project = self.identity_module.find_mandatory_project.return_value

        self.mocked_connection.assert_called_once_with(cloud)
        self.network_api.security_groups.assert_called_once_with(
            tenant_id=found_project.id
        )
        assert return_val == list(self.network_api.security_groups.return_value)

    @raises(MissingMandatoryParamError)
    def test_create_security_group_missing_name_raises(self):
        """
        Test that the security group identifier is correctly checked
        """
        self.instance.create_security_group(
            cloud_account=NonCallableMock(),
            group_description=NonCallableMock(),
            project_identifier=NonCallableMock(),
            group_name=" \t",
        )

    def test_create_security_group_forwards_result(self):
        """
        Tests find create group forwards the new group
        """
        cloud, name, description, project = (NonCallableMock() for _ in range(4))
        result = self.instance.create_security_group(cloud, name, description, project)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, project
        )
        self.mocked_connection.assert_called_once_with(cloud)
        self.network_api.create_security_group.assert_called_once_with(
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            name=name.strip(),
            description=description,
        )
        assert result == self.network_api.create_security_group.return_value

    @raises(ItemNotFoundError)
    def test_create_rule_group_not_found_raises(self):
        """
        Tests that create security group rule raises if not security group is found
        """
        self.instance.find_security_group = Mock(return_value=None)
        self.instance.create_security_group_rule(NonCallableMock(), NonCallableMock())

    @parameterized.expand([(1, ""), ("", 1)])
    def test_create_rule_throws_for_missing_port(self, start_port, end_port):
        """
        Tests that missing port starting values throw
        """
        mocked_details = NonCallableMock()
        mocked_details.port_range = (start_port, end_port)
        with assert_raises(ValueError):
            self.instance.create_security_group_rule(NonCallableMock(), mocked_details)

    @raises(ValueError)
    def test_create_rule_throws_for_missing_port_end(self):
        """
        Tests that missing port final values throw
        """
        mocked_details = NonCallableMock()
        mocked_details.port_range = (1, None)
        self.instance.create_security_group_rule(NonCallableMock(), mocked_details)

    @parameterized.expand([(1, "a"), ("d", 2), ("*a", "a"), ("*", "*1")])
    def test_create_rule_throws_non_numeric(self, start_port, end_port):
        """
        Tests that non-numeric inputs throw
        """
        mocked_details = NonCallableMock()
        mocked_details.port_range = (start_port, end_port)
        with assert_raises(ValueError):
            self.instance.create_security_group_rule(NonCallableMock(), mocked_details)

    def test_create_rule_forwards_result(self):
        """
        Tests that create rule returns the new rule
        """
        cloud, mock_details = NonCallableMock(), NonCallableMagicMock()
        mock_details.port_range = (0, 0)
        self.instance.find_security_group = Mock()
        returned = self.instance.create_security_group_rule(cloud, mock_details)

        self.instance.find_security_group.assert_called_once_with(
            cloud,
            mock_details.project_identifier,
            mock_details.security_group_identifier,
        )
        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, mock_details.project_identifier
        )

        self.network_api.create_security_group_rule.assert_called_once_with(
            project_id=self.identity_module.find_mandatory_project.return_value.id,
            security_group_id=self.instance.find_security_group.return_value.id,
            direction=mock_details.direction.value.lower(),
            ether_type=mock_details.ip_version.value.lower(),
            protocol=mock_details.protocol.value.lower(),
            remote_ip_prefix=mock_details.remote_ip_cidr,
            port_range_min=str(mock_details.port_range[0]),
            port_range_max=str(mock_details.port_range[1]),
        )
        assert returned == self.network_api.create_security_group_rule.return_value

    def test_create_port_wildcard(self):
        """
        Tests create port will accept and convert a wildcard correctly
        """
        cloud, mock_details = NonCallableMock(), NonCallableMagicMock()
        mock_details.protocol = Protocol.ANY
        mock_details.port_range = ("*", "*")

        self.instance.create_security_group_rule(cloud, mock_details)
        self.network_api.create_security_group_rule.assert_called_once_with(
            project_id=ANY,
            security_group_id=ANY,
            direction=ANY,
            ether_type=ANY,
            remote_ip_prefix=ANY,
            protocol=None,
            port_range_min=None,
            port_range_max=None,
        )

    # pylint:disable=too-many-arguments
    @parameterized.expand(
        [
            (
                NetworkDirection.INGRESS,
                IPVersion.IPV4,
                Protocol.ICMP,
                "0.0.0.0/0",
                ("*", "*"),
            ),
            (
                NetworkDirection.INGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "0.0.0.0/0",
                ("22", "22"),
            ),
            (
                NetworkDirection.EGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "130.246.0.0/16",
                ("53", "53"),
            ),
            (
                NetworkDirection.INGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "130.246.0.0/16",
                ("53", "53"),
            ),
            (
                NetworkDirection.EGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "130.246.180.101/32",
                ("80", "80"),
            ),
            (
                NetworkDirection.EGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "130.246.180.163/32",
                ("80", "80"),
            ),
            (
                NetworkDirection.INGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "130.246.180.13/32",
                ("80", "80"),
            ),
            (
                NetworkDirection.EGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "130.246.180.13/32",
                ("80", "80"),
            ),
            (
                NetworkDirection.INGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "130.246.223.126/32",
                ("80", "9999"),
            ),
            (
                NetworkDirection.INGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "130.246.180.101/32",
                ("80", "80"),
            ),
            (
                NetworkDirection.INGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "130.246.186.163/32",
                ("80", "80"),
            ),
            (
                NetworkDirection.EGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "130.246.180.101/32",
                ("443", "443"),
            ),
            (
                NetworkDirection.EGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "130.246.223.126/32",
                ("9999", "9999"),
            ),
            (
                NetworkDirection.EGRESS,
                IPVersion.IPV4,
                Protocol.UDP,
                "130.246.0.0/16",
                ("53", "53"),
            ),
            (
                NetworkDirection.INGRESS,
                IPVersion.IPV4,
                Protocol.UDP,
                "130.246.0.0/16",
                ("53", "53"),
            ),
            (
                NetworkDirection.EGRESS,
                IPVersion.IPV4,
                Protocol.TCP,
                "130.246.176.0/22",
                ("443", "443"),
            ),
        ]
    )
    def test_create_external_rules_default_rules(
        self,
        direction,
        ip_version,
        protocol,
        remote_ip_cidr,
        port_range,
    ):
        """
        Tests that specific rules are created for external security groups
        """
        cloud, project_identifier, security_group_identifier = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        self.instance.create_security_group_rule = Mock()
        self.instance.create_external_security_group_rules(
            cloud, project_identifier, security_group_identifier
        )
        self.instance.create_security_group_rule.assert_any_call(
            cloud,
            SecurityGroupRuleDetails(
                security_group_identifier=security_group_identifier,
                project_identifier=project_identifier,
                direction=direction,
                ip_version=ip_version,
                protocol=protocol,
                remote_ip_cidr=remote_ip_cidr,
                port_range=port_range,
            ),
        )

    @parameterized.expand(
        [
            "8.0.0.0/7",
            "192.170.0.0/15",
            "172.64.0.0/10",
            "192.160.0.0/13",
            "192.169.0.0/16",
            "192.176.0.0/12",
            "192.128.0.0/11",
            "173.0.0.0/8",
            "172.0.0.0/12",
            "130.248.0.0/12",
            "193.0.0.0/8",
            "130.247.0.0/16",
            "32.0.0.0/3",
            "131.0.0.0/8",
            "196.0.0.0/6",
            "176.0.0.0/4",
            "128.0.0.0/7",
            "174.0.0.0/7",
            "144.0.0.0/4",
            "172.128.0.0/9",
            "192.172.0.0/14",
            "192.192.0.0/10",
            "208.0.0.0/4",
            "194.0.0.0/7",
            "168.0.0.0/6",
            "132.0.0.0/6",
            "192.0.0.0/9",
            "160.0.0.0/5",
            "172.32.0.0/11",
            "12.0.0.0/6",
            "16.0.0.0/4",
            "130.128.0.0/10",
            "130.224.0.0/12",
            "130.0.0.0/9",
            "64.0.0.0/2",
            "130.244.0.0/15",
            "200.0.0.0/5",
            "130.240.0.0/14",
            "11.0.0.0/8",
            "130.192.0.0/11",
            "136.0.0.0/5",
            "0.0.0.0/5",
        ]
    )
    def test_create_external_rules_tcp_udp_cidrs(self, cidr):
        """
        Tests that tcp and udp egress rules created for a set of cidrs
        """
        cloud, project_identifier, security_group_identifier = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        self.instance.create_security_group_rule = Mock()
        self.instance.create_external_security_group_rules(
            cloud, project_identifier, security_group_identifier
        )
        self.instance.create_security_group_rule.assert_any_call(
            cloud,
            SecurityGroupRuleDetails(
                security_group_identifier=security_group_identifier,
                project_identifier=project_identifier,
                direction=NetworkDirection.EGRESS,
                ip_version=IPVersion.IPV4,
                protocol=Protocol.TCP,
                remote_ip_cidr=cidr,
                port_range=("1", "65535"),
            ),
        )

    def test_external_security_rules_count(self):
        """
        Tests number of external rules is as expected
        """
        self.instance.create_security_group_rule = Mock()
        cloud, project_identifier, security_group_identifier = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        self.instance.create_external_security_group_rules(
            cloud, project_identifier, security_group_identifier
        )

        assert self.instance.create_security_group_rule.call_count == 100
