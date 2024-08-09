from unittest.mock import MagicMock, NonCallableMock
import pytest

from enums.ip_version import IPVersion
from enums.network_direction import NetworkDirection
from enums.protocol import Protocol
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError

from openstack_api.openstack_security_groups import (
    create_external_security_group_rules,
    create_http_security_group,
    create_https_security_group,
    refresh_security_groups,
)
from structs.security_group_rule_details import SecurityGroupRuleDetails


@pytest.fixture(name="create_security_group_rule_test")
def run_create_security_group_rule_test():
    """runs a test to check if create_security_group_rule was called properly"""

    def test_case(mock_conn, mock_details: SecurityGroupRuleDetails):
        start_port, end_port = mock_details.port_range
        if mock_details.port_range == ("*", "*"):
            start_port, end_port = (None, None)

        mock_conn.network.create_security_group_rule.assert_any_call(
            project_id=mock_conn.identity.find_project.return_value.id,
            security_group_id=mock_conn.network.find_security_group.return_value.id,
            direction=mock_details.direction.value.lower(),
            ether_type=mock_details.ip_version.value.lower(),
            protocol=mock_details.protocol.value.lower(),
            remote_ip_prefix=mock_details.remote_ip_cidr,
            port_range_min=start_port,
            port_range_max=end_port,
        )

    return test_case


def test_create_http_security_group(create_security_group_rule_test):
    """test that create_http_security_group creates security group with appriopriate rules"""

    mock_conn = MagicMock()
    mock_project_identifier = "foo "
    create_http_security_group(mock_conn, mock_project_identifier)

    mock_conn.identity.find_project.assert_any_call("foo", ignore_missing=False)
    mock_conn.network.create_security_group.assert_called_once_with(
        name="HTTP",
        description="Rules allowing HTTP traffic ingress",
        project_id=mock_conn.identity.find_project.return_value.id,
    )
    create_security_group_rule_test(
        mock_conn,
        SecurityGroupRuleDetails(
            project_identifier="foo",
            security_group_identifier="HTTP",
            direction=NetworkDirection.INGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.TCP,
            remote_ip_cidr="0.0.0.0/0",
            port_range=("80", "80"),
        ),
    )


def test_create_http_security_group_invalid_project():
    """test that create_http_security_group raises error if project identifier missing"""
    mock_conn = MagicMock()
    mock_project_identifier = " \t"
    with pytest.raises(MissingMandatoryParamError):
        create_http_security_group(mock_conn, mock_project_identifier)
    mock_conn.network.create_security_group.assert_not_called()


def test_create_https_security_group(create_security_group_rule_test):
    """test that create_https_security_group creates security group with appriopriate rules"""

    mock_conn = MagicMock()
    mock_project_identifier = "foo "
    create_https_security_group(mock_conn, mock_project_identifier)

    mock_conn.identity.find_project.assert_any_call("foo", ignore_missing=False)
    mock_conn.network.create_security_group.assert_called_once_with(
        name="HTTPS",
        description="Rules allowing HTTPS traffic ingress",
        project_id=mock_conn.identity.find_project.return_value.id,
    )
    create_security_group_rule_test(
        mock_conn,
        SecurityGroupRuleDetails(
            project_identifier="foo",
            security_group_identifier="HTTPS",
            direction=NetworkDirection.INGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.TCP,
            remote_ip_cidr="0.0.0.0/0",
            port_range=("443", "443"),
        ),
    )
    create_security_group_rule_test(
        mock_conn,
        SecurityGroupRuleDetails(
            project_identifier="foo",
            security_group_identifier="HTTPS",
            direction=NetworkDirection.INGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.UDP,
            remote_ip_cidr="0.0.0.0/0",
            port_range=("443", "443"),
        ),
    )


def test_create_https_security_group_invalid_project():
    """test that create_https_security_group raises error if project identifier missing"""
    mock_conn = MagicMock()
    mock_project_identifier = " \t"
    with pytest.raises(MissingMandatoryParamError):
        create_https_security_group(mock_conn, mock_project_identifier)
    mock_conn.network.create_security_group.assert_not_called()


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    "direction, ip_version, protocol, remote_ip_cidr, port_range",
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
    ],
)
def test_create_external_rules_default_rules(
    direction,
    ip_version,
    protocol,
    remote_ip_cidr,
    port_range,
    create_security_group_rule_test,
):
    """
    Tests that specific rules are created for external security groups
    """
    mock_conn = MagicMock()
    mock_project_identifier = NonCallableMock()
    mock_security_group_identifier = NonCallableMock()

    create_external_security_group_rules(
        mock_conn, mock_project_identifier, mock_security_group_identifier
    )

    create_security_group_rule_test(
        mock_conn,
        SecurityGroupRuleDetails(
            security_group_identifier=mock_security_group_identifier,
            project_identifier=mock_project_identifier,
            direction=direction,
            ip_version=ip_version,
            protocol=protocol,
            remote_ip_cidr=remote_ip_cidr,
            port_range=port_range,
        ),
    )


@pytest.mark.parametrize(
    "cidr",
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
    ],
)
def test_create_external_rules_tcp_udp_cidrs(cidr, create_security_group_rule_test):
    """
    Tests that tcp and udp egress rules created for a set of cidrs
    """
    mock_conn = NonCallableMock()
    mock_project_identifier = NonCallableMock()
    mock_security_group_identifier = NonCallableMock()

    create_external_security_group_rules(
        mock_conn, mock_project_identifier, mock_security_group_identifier
    )
    create_security_group_rule_test(
        mock_conn,
        SecurityGroupRuleDetails(
            security_group_identifier=mock_security_group_identifier,
            project_identifier=mock_project_identifier,
            direction=NetworkDirection.EGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.TCP,
            remote_ip_cidr=cidr,
            port_range=("1", "65535"),
        ),
    )


def test_create_external_security_group_rules_invalid_project():
    """test that create_external_security_group_rules raises error if project identifier missing"""
    mock_conn = MagicMock()
    mock_project_identifier = " \t"
    mock_security_group_identifier = "foo"
    with pytest.raises(MissingMandatoryParamError):
        create_external_security_group_rules(
            mock_conn, mock_project_identifier, mock_security_group_identifier
        )
    mock_conn.network.create_security_group_rule.assert_not_called()


def test_create_external_security_group_rules_invalid_security_group():
    """test that create_external_security_group_rules raises error if security group identifier missing"""
    mock_conn = MagicMock()
    mock_project_identifier = "foo"
    mock_security_group_identifier = " \t"
    with pytest.raises(MissingMandatoryParamError):
        create_external_security_group_rules(
            mock_conn, mock_project_identifier, mock_security_group_identifier
        )
    mock_conn.network.create_security_group_rule.assert_not_called()


def test_refresh_security_groups():
    """test that refresh_security_groups works with valid project"""
    project_identifier = "foo"
    mock_conn = MagicMock()
    mock_conn.network.security_groups.return_value = ["bar"]
    result = refresh_security_groups(mock_conn, project_identifier)

    mock_conn.identity.find_project.assert_called_once_with(
        project_identifier, ignore_missing=False
    )
    mock_conn.network.security_groups.assert_called_once_with(
        tenant_id=mock_conn.identity.find_project.return_value.id
    )
    assert result == ["bar"]


def test_refresh_security_groups_invalid_project():
    """test that refresh_security_groups raises error with invalid project"""
    project_identifier = " \t"
    mock_conn = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        refresh_security_groups(mock_conn, project_identifier)
