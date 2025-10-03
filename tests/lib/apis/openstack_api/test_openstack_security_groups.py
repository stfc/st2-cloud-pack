import re
from unittest.mock import MagicMock, NonCallableMock

import pytest
from apis.openstack_api.enums.ip_version import IPVersion
from apis.openstack_api.enums.network_direction import NetworkDirection
from apis.openstack_api.enums.protocol import Protocol
from apis.openstack_api.openstack_security_groups import (
    _validate_rule_ports,
    create_external_security_group_rules,
    create_http_security_group,
    create_https_security_group,
    create_internal_security_group_rules,
    create_jasmin_security_group_rules,
    refresh_security_groups,
)
from apis.openstack_api.structs.security_group_rule_details import (
    SecurityGroupRuleDetails,
)
from meta.exceptions.missing_mandatory_param_error import MissingMandatoryParamError


@pytest.fixture(name="create_security_group_rule_test")
def run_create_security_group_rule_test():
    """runs a test to check if create_security_group_rule was called properly"""

    def test_case(mock_conn, mock_details: SecurityGroupRuleDetails):
        start_port, end_port = mock_details.port_range
        if mock_details.port_range == ("*", "*"):
            start_port, end_port = (None, None)

        mock_conn.identity.find_project.assert_any_call(
            mock_details.project_identifier.strip(), ignore_missing=False
        )

        mock_conn.network.find_security_group.assert_any_call(
            mock_details.security_group_identifier.strip(),
            ignore_missing=False,
            project_id=mock_conn.identity.find_project.return_value.id,
        )

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
        "0.0.0.0/5",
        "8.0.0.0/7",
        "11.0.0.0/8",
        "12.0.0.0/6",
        "17.0.0.0/4",
        "32.0.0.0/3",
        "64.0.0.0/2",
        "128.0.0.0/7",
        "130.0.0.0/9",
        "130.128.0.0/10",
        "130.192.0.0/11",
        "130.224.0.0/12",
        "130.240.0.0/14",
        "130.244.0.0/15",
        "130.247.0.0/16",
        "130.248.0.0/13",
        "131.0.0.0/8",
        "132.0.0.0/6",
        "136.0.0.0/5",
        "144.0.0.0/4",
        "160.0.0.0/5",
        "168.0.0.0/6",
        "172.0.0.0/12",
        "172.128.0.0/9",
        "172.32.0.0/11",
        "172.64.0.0/10",
        "173.0.0.0/8",
        "174.0.0.0/7",
        "176.0.0.0/4",
        "192.0.0.0/9",
        "192.128.0.0/11",
        "192.160.0.0/13",
        "192.169.0.0/16",
        "192.170.0.0/15",
        "192.172.0.0/14",
        "192.176.0.0/12",
        "192.192.0.0/10",
        "193.0.0.0/8",
        "194.0.0.0/7",
        "196.0.0.0/6",
        "200.0.0.0/5",
        "208.0.0.0/4",
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
            NetworkDirection.INGRESS,
            IPVersion.IPV4,
            Protocol.UDP,
            "0.0.0.0/0",
            ("7777", "7777"),
        ),
    ],
)
def test_create_internal_rules_default_rules(
    direction,
    ip_version,
    protocol,
    remote_ip_cidr,
    port_range,
    create_security_group_rule_test,
):
    """
    Tests that specific rules are created for internal security groups
    """
    mock_conn = MagicMock()
    mock_project_identifier = NonCallableMock()
    mock_security_group_identifier = NonCallableMock()

    create_internal_security_group_rules(
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


def test_create_internal_security_group_rules_invalid_project():
    """test that create_internal_security_group_rules raises error if project identifier missing"""
    mock_conn = MagicMock()
    mock_project_identifier = " \t"
    mock_security_group_identifier = "foo"
    with pytest.raises(MissingMandatoryParamError):
        create_internal_security_group_rules(
            mock_conn, mock_project_identifier, mock_security_group_identifier
        )
    mock_conn.network.create_security_group_rule.assert_not_called()


def test_create_internal_security_group_rules_invalid_security_group():
    """test that create_internal_security_group_rules raises error if security group identifier missing"""
    mock_conn = MagicMock()
    mock_project_identifier = "foo"
    mock_security_group_identifier = " \t"
    with pytest.raises(MissingMandatoryParamError):
        create_internal_security_group_rules(
            mock_conn, mock_project_identifier, mock_security_group_identifier
        )
    mock_conn.network.create_security_group_rule.assert_not_called()


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
            NetworkDirection.INGRESS,
            IPVersion.IPV4,
            Protocol.UDP,
            "0.0.0.0/0",
            ("7777", "7777"),
        ),
    ],
)
def test_create_jasmin_rules_default_rules(
    direction,
    ip_version,
    protocol,
    remote_ip_cidr,
    port_range,
    create_security_group_rule_test,
):
    """
    Tests that specific rules are created for jasmin security groups
    """
    mock_conn = MagicMock()
    mock_project_identifier = NonCallableMock()
    mock_security_group_identifier = NonCallableMock()

    create_jasmin_security_group_rules(
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


def test_create_jasmin_security_group_rules_invalid_project():
    """test that create_jasmin_security_group_rules raises error if project identifier missing"""
    mock_conn = MagicMock()
    mock_project_identifier = " \t"
    mock_security_group_identifier = "foo"
    with pytest.raises(MissingMandatoryParamError):
        create_jasmin_security_group_rules(
            mock_conn, mock_project_identifier, mock_security_group_identifier
        )
    mock_conn.network.create_security_group_rule.assert_not_called()


def test_create_jasmin_security_group_rules_invalid_security_group():
    """test that create_jasmin_security_group_rules raises error if security group identifier missing"""
    mock_conn = MagicMock()
    mock_project_identifier = "foo"
    mock_security_group_identifier = " \t"
    with pytest.raises(MissingMandatoryParamError):
        create_jasmin_security_group_rules(
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


@pytest.mark.parametrize(
    "start_port, end_port, expected_exception, expected_message",
    [
        (
            "80",
            "80",
            None,
            None,
        ),
        (
            "*",
            "*",
            None,
            None,
        ),
        (
            "80",
            "*",
            None,
            None,
        ),
        (
            "*",
            "80",
            None,
            None,
        ),
        (
            "",
            "80",
            ValueError,
            "A starting and ending port must both be provided",
        ),
        (
            "80",
            "",
            ValueError,
            "A starting and ending port must both be provided",
        ),
        (
            "foo",
            "80",
            ValueError,
            re.escape("The starting port must be an integer or '*'. Got foo"),
        ),
        (
            "80",
            "bar",
            ValueError,
            re.escape("The end port must be an integer or '*'. Got bar"),
        ),
    ],
)
def test_validate_rule_ports(
    start_port, end_port, expected_exception, expected_message
):
    """
    Test the _validate_rule_ports function with various valid and invalid inputs.
    """
    if expected_exception:
        with pytest.raises(expected_exception, match=expected_message):
            _validate_rule_ports(start_port, end_port)
    else:
        # A simple check to ensure no exception is raised
        _validate_rule_ports(start_port, end_port)
