from typing import Optional, List
from openstack.connection import Connection

from openstack.network.v2.floating_ip import FloatingIP
from openstack.network.v2.network import Network
from openstack.network.v2.rbac_policy import RBACPolicy

from enums.rbac_network_actions import RbacNetworkActions
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError

from structs.network_details import NetworkDetails
from structs.network_rbac import NetworkRbac


def allocate_floating_ips(
    conn: Connection,
    network_identifier: str,
    project_identifier: str,
    number_to_create: int,
) -> List[FloatingIP]:
    """
    Allocates floating IPs to a given project
    :param conn: openstack connection object
    :param network_identifier: ID or Name of network to allocate from,
    :param project_identifier: ID or Name of project to allocate to,
    :param number_to_create: Number of floating ips to create
    :return: List of all allocated floating IPs
    """
    project_identifier = project_identifier.strip()
    if not project_identifier:
        raise MissingMandatoryParamError("A project name or ID is required")

    network_identifier = network_identifier.strip()
    if not network_identifier:
        raise MissingMandatoryParamError("A network name or ID is required")

    project = conn.identity.find_project(project_identifier, ignore_missing=False)
    network = conn.network.find_network(network_identifier, ignore_missing=False)

    return [
        conn.network.create_ip(project_id=project.id, floating_network_id=network.id)
        for _ in range(number_to_create)
    ]


def create_network(conn: Connection, details: NetworkDetails) -> Optional[Network]:
    """
    Creates a network for a given project
    :param conn: openstack connection object
    :param details: A struct containing all details related to this new network
    :return: A Network object, or None
    """
    details.name = details.name.strip()
    if not details.name:
        raise MissingMandatoryParamError("A name for the new network is required")

    details.project_identifier = details.project_identifier.strip()
    if not details.project_identifier:
        raise MissingMandatoryParamError("A project name or ID is required")

    project = conn.identity.find_project(
        details.project_identifier, ignore_missing=False
    )

    return conn.network.create_network(
        project_id=project.id,
        name=details.name,
        description=details.description,
        provider_network_type=details.provider_network_type.value.lower(),
        is_port_security_enabled=details.port_security_enabled,
        is_router_external=details.has_external_router,
    )


def delete_network(conn: Connection, network_identifier: str) -> bool:
    """
    Deletes the specified network
    :param conn: openstack connection object
    :param network_identifier: The name or Openstack ID to use
    :return: True if deleted, else False
    """
    network_identifier = network_identifier.strip()
    if not network_identifier:
        raise MissingMandatoryParamError("A network name or ID is required")

    network = conn.network.find_network(network_identifier, ignore_missing=False)

    result = conn.network.delete_network(network, ignore_missing=False)
    return result is None  # None == success


def create_network_rbac(conn: Connection, rbac_details: NetworkRbac) -> RBACPolicy:
    """
    Creates an RBAC policy for the given network
    :param conn: openstack connection object
    :param rbac_details: The details associated with the new policy
    :return: The RBAC Policy if it was created, else None
    """
    rbac_details.network_identifier = rbac_details.network_identifier.strip()
    if not rbac_details.network_identifier:
        raise MissingMandatoryParamError("A network name or ID is required")

    rbac_details.project_identifier = rbac_details.project_identifier.strip()
    if not rbac_details.project_identifier:
        raise MissingMandatoryParamError("A project name or ID is required")

    network = conn.network.find_network(
        rbac_details.network_identifier, ignore_missing=False
    )
    project = conn.identity.find_project(
        rbac_details.project_identifier, ignore_missing=False
    )

    return conn.network.create_rbac_policy(
        object_id=network.id,
        # We only support network RBAC policies at the moment
        object_type="network",
        target_project_id=project.id,
        action=_parse_rbac_action(rbac_details.action),
    )


def _parse_rbac_action(action: RbacNetworkActions) -> str:
    """
    Parses the given RBAC enum into an Openstack compatible string
    """
    # This can be replaced with match case when we're Python 3.10+
    if action is RbacNetworkActions.SHARED:
        return "access_as_shared"
    if action is RbacNetworkActions.EXTERNAL:
        return "access_as_external"
    raise KeyError("Unknown RBAC action")


def delete_network_rbac(conn: Connection, rbac_identifier: str) -> bool:
    """
    Deletes the specified network
    :param conn: openstack connection object
    :param rbac_identifier: The name or Openstack ID to use
    :return: True if deleted, else False
    """
    raise NotImplementedError("Pending better RBAC search")
