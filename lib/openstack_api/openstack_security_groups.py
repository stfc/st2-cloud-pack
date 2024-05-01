from typing import Optional, List

from openstack.network.v2.security_group import SecurityGroup
from openstack.network.v2.security_group_rule import SecurityGroupRule

from enums.ip_version import IPVersion
from enums.network_direction import NetworkDirection
from enums.protocol import Protocol
from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from structs.security_group_rule_details import SecurityGroupRuleDetails


class OpenstackSecurityGroups(OpenstackWrapperBase):
    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(self._connection_cls)

    def create_external_security_group_rules(
        self, cloud_account, project_identifier, security_group_identifier
    ):
        """
        Sets external security group rules
        :param cloud_account: The associated clouds.yaml account
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
                self.create_security_group_rule(
                    cloud_account,
                    SecurityGroupRuleDetails(
                        security_group_identifier=security_group_identifier,
                        project_identifier=project_identifier,
                        **rule,
                    ),
                )
            )
        for cidr in tcp_udp_egress_external_cidr:
            results.append(
                self.create_security_group_rule(
                    cloud_account,
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
                self.create_security_group_rule(
                    cloud_account,
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

    def find_security_group(
        self,
        cloud_account: str,
        project_identifier: str,
        security_group_identifier: str,
    ) -> Optional[SecurityGroup]:
        """
        Finds a given security group
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The name or Openstack ID of the associated project
        :param security_group_identifier: The name or Openstack ID of the associated security group
        :return: The security group if found
        """
        security_group_identifier = security_group_identifier.strip()
        if not security_group_identifier:
            raise MissingMandatoryParamError("A security group identifier is required")

        project = self._identity_api.find_mandatory_project(
            cloud_account, project_identifier
        )

        with self._connection_cls(cloud_account) as conn:
            return conn.network.find_security_group(
                security_group_identifier, project_id=project.id, ignore_missing=True
            )

    def search_security_group(
        self, cloud_account: str, project_identifier: str
    ) -> List[SecurityGroup]:
        """
        Returns a list of security groups associated with an account
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated security groups with
        :return: A list of all security groups
        """
        project = self._identity_api.find_mandatory_project(
            cloud_account, project_identifier=project_identifier
        )
        with self._connection_cls(cloud_account) as conn:
            # We have to use tenant_id here to force Train to
            # actually refresh the default security group for a new project
            return list(conn.network.security_groups(tenant_id=project.id))

    def create_security_group(
        self,
        cloud_account: str,
        group_name: str,
        group_description: str,
        project_identifier: str,
    ) -> SecurityGroup:
        """
        Creates a new security group in the given project
        :param cloud_account: The associated clouds.yaml account
        :param group_name: The new security group name
        :param group_description: The new security group description
        :param project_identifier: The name or ID of the project to create a security group in
        :return: The created security group
        """
        group_name = group_name.strip()
        if not group_name:
            raise MissingMandatoryParamError(
                "A group name is required for the new security group"
            )

        project = self._identity_api.find_mandatory_project(
            cloud_account, project_identifier
        )
        with self._connection_cls(cloud_account) as conn:
            return conn.network.create_security_group(
                name=group_name,
                description=group_description,
                project_id=project.id,
            )

    def create_security_group_rule(
        self, cloud_account: str, details: SecurityGroupRuleDetails
    ) -> SecurityGroupRule:
        """
        :param cloud_account: The associated clouds.yaml account
        :param details: The details of the new security group rule
        :return: The created rule
        """
        security_group = self.find_security_group(
            cloud_account, details.project_identifier, details.security_group_identifier
        )
        if not security_group:
            raise ItemNotFoundError(
                f'The security group "{details.security_group_identifier}" was not found'
            )

        start_port = str(details.port_range[0]).strip()
        end_port = str(details.port_range[1]).strip()
        self._validate_rule_ports(start_port, end_port)

        # Map any values to None custom_types as per OS API
        protocol = (
            None if details.protocol is Protocol.ANY else details.protocol.value.lower()
        )
        start_port = None if start_port == "*" else start_port
        end_port = None if end_port == "*" else end_port

        project = self._identity_api.find_mandatory_project(
            cloud_account, details.project_identifier
        )

        with self._connection_cls(cloud_account) as conn:
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

    @staticmethod
    def _validate_rule_ports(start_port: str, end_port: str):
        if len(start_port) == 0 or len(end_port) == 0:
            raise ValueError("A starting and ending port must both be provided")
        if not start_port.isdigit() and start_port != "*":
            raise ValueError(
                f"The starting port must be an integer or '*'. Got {start_port}"
            )
        if not end_port.isdigit() and end_port != "*":
            raise ValueError(f"The end port must be an integer or '*'. Got {end_port}")
