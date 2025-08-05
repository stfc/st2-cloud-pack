import logging
from openstack.connection import Connection
from openstack.network.v2.router import Router
from apis.openstack_api.structs.router_details import RouterDetails

from meta.exceptions.missing_mandatory_param_error import MissingMandatoryParamError

logger = logging.getLogger(__name__)


def add_interface_to_router(
    conn: Connection,
    project_identifier: str,
    router_identifier: str,
    subnet_identifier: str,
) -> Router:
    """
    Adds a subnet to a given router
    :param conn: openstack connection object
    :param project_identifier: The name or ID of the project containing the router and subnet
    :param router_identifier: The name or ID of the router to add an interface to
    :param subnet_identifier: The subnet name or ID of the router to add an interface to
    :return: The router the subnet was added to
    """
    project_identifier = project_identifier.strip()
    if not project_identifier:
        raise MissingMandatoryParamError("A project name or ID is required")

    router_identifier = router_identifier.strip()
    if not router_identifier:
        raise MissingMandatoryParamError("A router name or ID is required")

    subnet_identifier = subnet_identifier.strip()
    if not subnet_identifier:
        raise MissingMandatoryParamError("A subnet name or ID is required")

    project = conn.identity.find_project(project_identifier, ignore_missing=False)
    router = conn.network.find_router(
        router_identifier, project_id=project.id, ignore_missing=False
    )
    subnet = conn.network.find_subnet(
        subnet_identifier, project_id=project.id, ignore_missing=False
    )

    conn.network.add_interface_to_router(router=router, subnet_id=subnet.id)
    return router


def create_router(conn: Connection, details: RouterDetails) -> Router:
    """
    Creates a router for the given project without any internal interfaces
    :param conn: openstack connection object
    :param details: The details of the router to create
    """
    details.project_identifier = details.project_identifier.strip()
    if not details.project_identifier:
        raise MissingMandatoryParamError("A project name or ID is required")

    details.external_gateway = details.external_gateway.strip()
    if not details.external_gateway:
        raise MissingMandatoryParamError(
            "External gateway network's name or ID is required"
        )

    details.router_name = details.router_name.strip()
    if not details.router_name:
        raise MissingMandatoryParamError("New router name is required")

    project = conn.identity.find_project(
        details.project_identifier, ignore_missing=False
    )
    external_network = conn.network.find_network(
        details.external_gateway, ignore_missing=False
    )

    return conn.network.create_router(
        project_id=project.id,
        name=details.router_name,
        description=details.router_description,
        external_gateway_info={"network_id": external_network.id},
        is_distributed=details.is_distributed,
        is_ha=True,
    )


def check_for_internal_routers(conn: Connection):
    """
    Check for routers with gateway address on the internal network

    :param conn: Openstack connection
    :type conn: Connection
    :return: List of routers objects
    """

    def get_gateway_ips_from_router(router: Router):
        """
        Returns the gateway ips of a router
        """
        if not router.external_gateway_info:
            return []
        ips = []
        for i in router.external_gateway_info.get("external_fixed_ips"):
            ips.append(i["ip_address"])
        return ips

    routers_with_internal_gateway = []
    for router in conn.network.routers():
        logger.info("checking router %s", router.id)
        ips = get_gateway_ips_from_router(router)
        for ip in ips:
            if ip.startswith("172.16"):
                routers_with_internal_gateway.append(router)
                logger.error("Address: %s Router UUID: %s", ip, router.id)

    return routers_with_internal_gateway
