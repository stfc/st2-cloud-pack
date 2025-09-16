from typing import List

from openstack.connection import Connection

from openstack.network.v2.security_group import SecurityGroup
from openstack.network.v2.security_group_rule import SecurityGroupRule

from apis.openstack_api.enums.ip_version import IPVersion
from apis.openstack_api.enums.network_direction import NetworkDirection
from apis.openstack_api.enums.protocol import Protocol
from apis.openstack_api.structs.security_group_rule_details import (
    SecurityGroupRuleDetails,
)

from meta.exceptions.missing_mandatory_param_error import MissingMandatoryParamError


def create_http_security_group(conn, project_identifier: str):
    """
    Create a security group with default HTTP rules setup
    :param conn: openstack connection object
    :param project_identifier: Name or ID of project to create rules on
    """
    _create_security_group(
        conn, "HTTP", "Rules allowing HTTP traffic ingress", project_identifier
    )
    _create_security_group_rule(
        conn,
        SecurityGroupRuleDetails(
            project_identifier=project_identifier,
            security_group_identifier="HTTP",
            direction=NetworkDirection.INGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.TCP,
            remote_ip_cidr="0.0.0.0/0",
            port_range=("80", "80"),
        ),
    )


def create_https_security_group(conn, project_identifier: str):
    """
    Create a security group with default HTTPS rules setup
    :param conn: openstack connection object
    :param project_identifier: Name or ID of project to create rules on
    """
    _create_security_group(
        conn, "HTTPS", "Rules allowing HTTPS traffic ingress", project_identifier
    )
    _create_security_group_rule(
        conn,
        SecurityGroupRuleDetails(
            project_identifier=project_identifier,
            security_group_identifier="HTTPS",
            direction=NetworkDirection.INGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.TCP,
            remote_ip_cidr="0.0.0.0/0",
            port_range=("443", "443"),
        ),
    )
    _create_security_group_rule(
        conn,
        SecurityGroupRuleDetails(
            project_identifier=project_identifier,
            security_group_identifier="HTTPS",
            direction=NetworkDirection.INGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.UDP,
            remote_ip_cidr="0.0.0.0/0",
            port_range=("443", "443"),
        ),
    )


def create_external_security_group_rules(
    conn, project_identifier, security_group_identifier
):
    """
    Sets external security group rules
    :param conn: openstack connection object
    :param project_identifier: the name or the Openstack ID of the associated project
    :param security_group_identifier: The name or the Openstack ID of the associated security group
    """
    # default network external rules
    default_external_rules = [
        {
            "direction": NetworkDirection.INGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.ICMP,
            "remote_ip_cidr": "0.0.0.0/0",
            "port_range": ("*", "*"),
        },
        {
            "direction": NetworkDirection.INGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "0.0.0.0/0",
            "port_range": ("22", "22"),
        },
        {
            "direction": NetworkDirection.EGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "130.246.0.0/16",
            "port_range": ("53", "53"),
        },
        {
            "direction": NetworkDirection.INGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "130.246.0.0/16",
            "port_range": ("53", "53"),
        },
        {
            "direction": NetworkDirection.EGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "130.246.180.101/32",
            "port_range": ("80", "80"),
        },
        {
            "direction": NetworkDirection.EGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "130.246.180.163/32",
            "port_range": ("80", "80"),
        },
        {
            "direction": NetworkDirection.INGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "130.246.180.13/32",
            "port_range": ("80", "80"),
        },
        {
            "direction": NetworkDirection.EGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "130.246.180.13/32",
            "port_range": ("80", "80"),
        },
        {
            "direction": NetworkDirection.INGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "130.246.223.126/32",
            "port_range": ("80", "9999"),
        },
        {
            "direction": NetworkDirection.INGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "130.246.180.101/32",
            "port_range": ("80", "80"),
        },
        {
            "direction": NetworkDirection.INGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "130.246.186.163/32",
            "port_range": ("80", "80"),
        },
        {
            "direction": NetworkDirection.EGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "130.246.180.101/32",
            "port_range": ("443", "443"),
        },
        {
            "direction": NetworkDirection.EGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "130.246.223.126/32",
            "port_range": ("9999", "9999"),
        },
        {
            "direction": NetworkDirection.EGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.UDP,
            "remote_ip_cidr": "130.246.0.0/16",
            "port_range": ("53", "53"),
        },
        {
            "direction": NetworkDirection.INGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.UDP,
            "remote_ip_cidr": "130.246.0.0/16",
            "port_range": ("53", "53"),
        },
        {
            "direction": NetworkDirection.EGRESS,
            "ip_version": IPVersion.IPV4,
            "protocol": Protocol.TCP,
            "remote_ip_cidr": "130.246.176.0/22",
            "port_range": ("443", "443"),
        },
    ]

    # tcp/udp egress external cidr
    tcp_udp_egress_external_cidr = [
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

    results = []
    for rule in default_external_rules:
        results.append(
            _create_security_group_rule(
                conn,
                SecurityGroupRuleDetails(
                    security_group_identifier=security_group_identifier,
                    project_identifier=project_identifier,
                    **rule,
                ),
            )
        )
    for cidr in tcp_udp_egress_external_cidr:
        results.append(
            _create_security_group_rule(
                conn,
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
        )
        results.append(
            _create_security_group_rule(
                conn,
                SecurityGroupRuleDetails(
                    security_group_identifier=security_group_identifier,
                    project_identifier=project_identifier,
                    direction=NetworkDirection.EGRESS,
                    ip_version=IPVersion.IPV4,
                    protocol=Protocol.UDP,
                    remote_ip_cidr=cidr,
                    port_range=("1", "65535"),
                ),
            )
        )
    return results


def create_internal_security_group_rules(
    conn: Connection, project_identifier: str, security_group_identifier: str
):
    """
    Sets internal security group rules
    :param conn: openstack connection object
    :param project_identifier: the name or the Openstack ID of the associated project
    :param security_group_identifier: The name or the Openstack ID of the associated security group
    """

    # allow all icmp by default
    _create_security_group_rule(
        conn,
        SecurityGroupRuleDetails(
            project_identifier=project_identifier,
            security_group_identifier=security_group_identifier,
            direction=NetworkDirection.INGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.ICMP,
            remote_ip_cidr="0.0.0.0/0",
            port_range=("*", "*"),
        ),
    )

    # allow ssh by default
    _create_security_group_rule(
        conn,
        SecurityGroupRuleDetails(
            project_identifier=project_identifier,
            security_group_identifier=security_group_identifier,
            direction=NetworkDirection.INGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.TCP,
            remote_ip_cidr="0.0.0.0/0",
            port_range=("22", "22"),
        ),
    )

    # allow aquilon notify by default
    _create_security_group_rule(
        conn,
        SecurityGroupRuleDetails(
            project_identifier=project_identifier,
            security_group_identifier=security_group_identifier,
            direction=NetworkDirection.INGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.UDP,
            remote_ip_cidr="0.0.0.0/0",
            port_range=("7777", "7777"),
        ),
    )


def create_jasmin_security_group_rules(
    conn: Connection, project_identifier: str, security_group_identifier: str
):
    """
    Sets jasmin related security group rules
    :param conn: openstack connection object
    :param project_identifier: the name or the Openstack ID of the associated project
    :param security_group_identifier: The name or the Openstack ID of the associated security group
    """

    # allow all icmp by default
    _create_security_group_rule(
        conn,
        SecurityGroupRuleDetails(
            project_identifier=project_identifier,
            security_group_identifier=security_group_identifier,
            direction=NetworkDirection.INGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.ICMP,
            remote_ip_cidr="0.0.0.0/0",
            port_range=("*", "*"),
        ),
    )

    # allow ssh by default
    _create_security_group_rule(
        conn,
        SecurityGroupRuleDetails(
            project_identifier=project_identifier,
            security_group_identifier=security_group_identifier,
            direction=NetworkDirection.INGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.TCP,
            remote_ip_cidr="0.0.0.0/0",
            port_range=("22", "22"),
        ),
    )

    # allow aquilon notify by default
    _create_security_group_rule(
        conn,
        SecurityGroupRuleDetails(
            project_identifier=project_identifier,
            security_group_identifier=security_group_identifier,
            direction=NetworkDirection.INGRESS,
            ip_version=IPVersion.IPV4,
            protocol=Protocol.UDP,
            remote_ip_cidr="0.0.0.0/0",
            port_range=("7777", "7777"),
        ),
    )


def refresh_security_groups(
    conn: Connection, project_identifier: str
) -> List[SecurityGroup]:
    """
    Refresh security groups so they'll get created when a new project is created
    :param conn: openstack connection object
    :param project_identifier: The project to get all associated security groups with
    :return: A list of all security groups
    """
    project_identifier = project_identifier.strip()
    if not project_identifier:
        raise MissingMandatoryParamError("A project name or ID is required")
    project = conn.identity.find_project(project_identifier, ignore_missing=False)

    # We have to use tenant_id here to force Train to
    # actually refresh the default security group for a new project
    return list(conn.network.security_groups(tenant_id=project.id))


def _create_security_group(
    conn: Connection,
    group_name: str,
    group_description: str,
    project_identifier: str,
) -> SecurityGroup:
    """
    Creates a new security group in the given project
    :param conn: openstack connection object
    :param group_name: The new security group name
    :param group_description: The new security group description
    :param project_identifier: The name or ID of the project to create a security group in
    :return: The created security group
    """
    project_identifier = project_identifier.strip()
    if not project_identifier:
        raise MissingMandatoryParamError("A project name or ID is required")
    project = conn.identity.find_project(project_identifier, ignore_missing=False)

    return conn.network.create_security_group(
        name=group_name,
        description=group_description,
        project_id=project.id,
    )


def _create_security_group_rule(
    conn: Connection, details: SecurityGroupRuleDetails
) -> SecurityGroupRule:
    """
    :param conn: openstack connection object
    :param details: The details of the new security group rule
    :return: The created rule
    """
    details.security_group_identifier = details.security_group_identifier.strip()
    if not details.security_group_identifier:
        raise MissingMandatoryParamError("A security group name or ID is required")

    details.project_identifier = details.project_identifier.strip()
    if not details.project_identifier:
        raise MissingMandatoryParamError("A project name or ID is required")
    project = conn.identity.find_project(
        details.project_identifier, ignore_missing=False
    )

    security_group = conn.network.find_security_group(
        details.security_group_identifier, ignore_missing=False, project_id=project.id
    )

    start_port = str(details.port_range[0]).strip()
    end_port = str(details.port_range[1]).strip()
    _validate_rule_ports(start_port, end_port)

    # Map any values to None custom_types as per OS API
    protocol = (
        None if details.protocol is Protocol.ANY else details.protocol.value.lower()
    )
    start_port = None if start_port == "*" else start_port
    end_port = None if end_port == "*" else end_port

    return conn.network.create_security_group_rule(
        project_id=project.id,
        security_group_id=security_group.id,
        direction=details.direction.value.lower(),
        ether_type=details.ip_version.value.lower(),
        protocol=protocol,
        remote_ip_prefix=details.remote_ip_cidr,
        port_range_min=start_port,
        port_range_max=end_port,
    )


def _validate_rule_ports(start_port: str, end_port: str):
    if len(start_port) == 0 or len(end_port) == 0:
        raise ValueError("A starting and ending port must both be provided")
    if not start_port.isdigit() and start_port != "*":
        raise ValueError(
            f"The starting port must be an integer or '*'. Got {start_port}"
        )
    if not end_port.isdigit() and end_port != "*":
        raise ValueError(f"The end port must be an integer or '*'. Got {end_port}")
