import logging
from typing import List, Optional

from apis.openstack_api.enums.network_providers import NetworkProviders
from apis.openstack_api.enums.networks import Networks
from apis.openstack_api.enums.rbac_network_actions import RbacNetworkActions
from apis.openstack_api.enums.user_domains import UserDomains
from apis.openstack_api.openstack_network import (
    create_network,
    create_network_rbac,
)
from apis.openstack_api.openstack_project import (
    create_project as create_openstack_project,
)
from apis.openstack_api.openstack_quota import set_quota
from apis.openstack_api.openstack_roles import assign_role_to_user
from apis.openstack_api.openstack_router import add_interface_to_router, create_router
from apis.openstack_api.openstack_security_groups import (
    create_external_security_group_rules,
    create_http_security_group,
    create_https_security_group,
    create_internal_security_group_rules,
    create_jasmin_security_group_rules,
    refresh_security_groups,
)
from apis.openstack_api.openstack_subnet import create_subnet
from apis.openstack_api.structs.network_details import NetworkDetails
from apis.openstack_api.structs.network_rbac import NetworkRbac
from apis.openstack_api.structs.project_details import ProjectDetails
from apis.openstack_api.structs.quota_details import QuotaDetails
from apis.openstack_api.structs.role_details import RoleDetails
from apis.openstack_api.structs.router_details import RouterDetails
from openstack.connection import Connection
from openstack.identity.v3.project import Project

logger = logging.getLogger(__name__)


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
def create_project(
    conn: Connection,
    project_name: str,
    project_email: str,
    project_description: str,
    user_domain: str,
    network: str,
    number_of_floating_ips: int = 1,
    number_of_security_group_rules: int = 200,
    project_immutable: Optional[bool] = False,
    parent_id: Optional[str] = None,
    admin_user_list: Optional[List[str]] = None,
    user_list: Optional[List[str]] = None,
):
    """
    Creates an OpenStack project.
    :param conn: OpenStack connection
    :type conn: Connection
    :param project_name: Project name
    :type project_name: str
    :param project_email: Contact email for project
    :type project_email: str
    :param project_description: Project description
    :type project_description: str
    :param user_domain: User domain
    :type user_domain: str
    :param network: Cloud network, e.g. Internal, External, JASMIN
    :type network: str
    :param number_of_floating_ips: Floating IP quota for project
    :type number_of_floating_ips: int
    :param number_of_security_group_rules: Security group quota for project
    :type number_of_security_group_rules: int
    :param project_immutable: Project is immutable or not
    :type project_immutable: bool
    :param parent_id: Project parent ID
    :type parent_id: str
    :param admin_user_list: List of project admin users
    :type admin_user_list: List[str]
    :param user_list: List of project users
    :type user_list: List[str]
    """
    if not admin_user_list:
        admin_user_list = []

    if not user_list:
        user_list = []

    project = create_openstack_project(
        conn,
        ProjectDetails(
            name=project_name,
            email=project_email,
            description=project_description,
            immutable=project_immutable,
            parent_id=parent_id,
            is_enabled=True,
        ),
    )

    # wait for default security group
    refresh_security_groups(conn, project["id"])

    network_type = Networks.from_string(network)

    set_quota(
        conn,
        QuotaDetails(
            project_identifier=project.id,
            floating_ips=number_of_floating_ips,
            security_group_rules=number_of_security_group_rules,
        ),
    )

    if network_type in (Networks.EXTERNAL, Networks.JASMIN):
        setup_external_networking(
            conn,
            project,
            network_type,
        )
    elif network_type == Networks.INTERNAL:
        setup_internal_networking(conn, project)
    else:
        raise NotImplementedError(f"Unknown networking type {network_type}")

    create_http_security_group(conn, project_identifier=project["id"])
    create_https_security_group(conn, project_identifier=project["id"])

    for admin_user in admin_user_list:
        assign_role_to_user(
            conn,
            RoleDetails(
                user_identifier=admin_user,
                user_domain=UserDomains.DEFAULT,
                project_identifier=project["id"],
                role_identifier="admin",
            ),
        )
        logger.info("Added %s as project admin", admin_user)

    for user in user_list:
        assign_role_to_user(
            conn,
            RoleDetails(
                user_identifier=user,
                user_domain=UserDomains.from_string(user_domain),
                project_identifier=project["id"],
                role_identifier="user",
            ),
        )
        logger.info("Added %s as project user", user)
    logger.info("Competed building project %s", project_name)


def setup_external_networking(
    conn: Connection,
    project: Project,
    external_network: Networks,
):
    """
    Setup the project's external networking.
    :param conn: OpenStack connection object
    :type conn: Connection
    :param project: OpenStack project object
    :type project: Project
    :param external_network: External Cloud network
    :type external_network: Networks
    """
    network = create_network(
        conn,
        NetworkDetails(
            name=f"{project.name}-network",
            description="",
            project_identifier=project.id,
            provider_network_type=NetworkProviders.VXLAN,
            port_security_enabled=True,
            has_external_router=False,
        ),
    )

    logger.info("Created network: %s", network.id)

    external_rbac_policy = create_network_rbac(
        conn,
        NetworkRbac(
            project_identifier=project.id,
            network_identifier=external_network.value,
            action=RbacNetworkActions.EXTERNAL,
        ),
    )

    logger.info("Created external network rbac: %s", external_rbac_policy.id)

    private_rbac_policy = create_network_rbac(
        conn,
        NetworkRbac(
            project_identifier=project.id,
            network_identifier=network.id,
            action=RbacNetworkActions.SHARED,
        ),
    )

    logger.info("Created private network rbac: %s", private_rbac_policy.id)

    router = create_router(
        conn,
        RouterDetails(
            router_name=f"{project.name}-router",
            router_description="",
            project_identifier=project.id,
            external_gateway=external_network.value,
            is_distributed=False,
        ),
    )

    logger.info("Created router: %s", router.id)

    subnet = create_subnet(
        conn,
        network_identifier=network.id,
        subnet_name=f"{project.name}-subnet",
        subnet_description="",
        dhcp_enabled=True,
    )

    logger.info("Created subnet: %s", subnet.id)

    add_interface_to_router(
        conn,
        project_identifier=project.id,
        router_identifier=router.id,
        subnet_identifier=subnet.id,
    )

    # create default security group rules
    if external_network == Networks.EXTERNAL:
        create_external_security_group_rules(
            conn, project_identifier=project.id, security_group_identifier="default"
        )
    elif external_network == Networks.JASMIN:
        create_jasmin_security_group_rules(
            conn, project_identifier=project.id, security_group_identifier="default"
        )
    else:
        raise NotImplementedError(f"Unknown external network type {external_network}")

    logger.info("Created default security group")


def setup_internal_networking(conn: Connection, project: Project):
    """
    Setup the project's internal networking.
    :param conn: OpenStack connection object
    :type conn: Connection
    :param project: OpenStack project object
    :type project: Project
    """
    create_network_rbac(
        conn,
        NetworkRbac(
            project_identifier=project["id"],
            network_identifier="Internal",
            action=RbacNetworkActions.SHARED,
        ),
    )

    # create default security group rules
    create_internal_security_group_rules(conn, project["id"], "default")
