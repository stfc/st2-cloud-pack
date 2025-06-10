from typing import Optional, List

from enums.network_providers import NetworkProviders
from enums.rbac_network_actions import RbacNetworkActions
from enums.user_domains import UserDomains

from openstack.connection import Connection
from openstack.identity.v3.project import Project

from openstack_api.openstack_network import (
    create_network,
    create_network_rbac,
    allocate_floating_ips,
)
from openstack_api.openstack_project import create_project as create_openstack_project
from openstack_api.openstack_quota import set_quota
from openstack_api.openstack_router import create_router, add_interface_to_router
from openstack_api.openstack_security_groups import (
    refresh_security_groups,
    create_https_security_group,
    create_http_security_group,
    create_external_security_group_rules,
    create_internal_security_group_rules,
)
from openstack_api.openstack_roles import assign_role_to_user
from openstack_api.openstack_subnet import create_subnet
from structs.network_details import NetworkDetails
from structs.network_rbac import NetworkRbac

from structs.project_details import ProjectDetails
from structs.quota_details import QuotaDetails
from structs.role_details import RoleDetails
from structs.router_details import RouterDetails


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
def create_project(
    conn: Connection,
    project_name: str,
    project_email: str,
    project_description: str,
    project_domain: str,
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
    :param project_domain: Project domain
    :type project_domain: str
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

    validate_jasmin_args(project_domain, user_domain, network)

    project = create_openstack_project(
        conn,
        ProjectDetails(
            name=project_name,
            email=project_email,
            description=project_description,
            project_domain=project_domain,
            immutable=project_immutable,
            parent_id=parent_id,
            is_enabled=True,
        ),
    )

    # wait for default security group
    refresh_security_groups(conn, project["id"])

    if network in ("External", "JASMIN External Cloud Network"):
        setup_external_networking(
            conn,
            project,
            network,
            number_of_floating_ips,
            number_of_security_group_rules,
        )
    elif network == "Internal":
        setup_internal_networking(conn, project)
    else:
        raise NotImplementedError(f"Unknown networking type {network}")

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

    for user in user_list:
        assign_role_to_user(
            conn,
            RoleDetails(
                user_identifier=user,
                user_domain=user_domain,
                project_identifier=project["id"],
                role_identifier="user",
            ),
        )


def validate_jasmin_args(project_domain: str, user_domain: str, network: str):
    """
    Validates that the given arguments are valid for a JASMIN project, i.e.
    if a JASMIN-specific argument has been supplied, the applicable arguments
    must match.
    :param project_domain: Project domain
    :type project_domain: str
    :param user_domain: User domain
    :type user_domain: str
    :param network: Cloud network
    :type network: str
    """
    args = [project_domain, user_domain, network]
    if any(input in ("jasmin", "JASMIN External Cloud Network") for input in args):
        if not all(
            (input in ("jasmin", "JASMIN External Cloud Network") for input in args)
        ):
            raise ValueError("Invalid input: JASMIN project/domain/network must match")


def setup_external_networking(
    conn: Connection,
    project: Project,
    external_network: str,
    number_of_floating_ips: int,
    number_of_security_group_rules: int,
):
    """
    Setup the project's external networking.
    :param conn: OpenStack connection object
    :type conn: Connection
    :param project: OpenStack project object
    :type project: Project
    :param external_network: External Cloud network
    :type external_network: str
    :param number_of_floating_ips: Floating IP quota for project
    :type number_of_floating_ips: int
    :param number_of_security_group_rules: Security group quota for project
    :type number_of_security_group_rules: int
    """
    network = create_network(
        conn,
        NetworkDetails(
            name=f"{project.name}-network",
            description="",
            project_identifier=project["id"],
            provider_network_type=NetworkProviders.VXLAN,
            port_security_enabled=True,
            has_external_router=False,
        ),
    )

    router = create_router(
        conn,
        RouterDetails(
            router_name=f"{project.name}-router",
            router_description="",
            project_identifier=project["id"],
            external_gateway=external_network,
            is_distributed=False,
        ),
    )

    subnet = create_subnet(
        conn,
        network_identifier=network["id"],
        subnet_name=f"{project.name}-subnet",
        subnet_description="",
        dhcp_enabled=True,
    )

    add_interface_to_router(
        conn,
        project_identifier=project["id"],
        router_identifier=router["id"],
        subnet_identifier=subnet["id"],
    )

    set_quota(
        conn,
        QuotaDetails(
            project_identifier=project["id"],
            num_floating_ips=number_of_floating_ips,
            num_security_group_rules=number_of_security_group_rules,
        ),
    )

    create_network_rbac(
        conn,
        NetworkRbac(
            project_identifier=project["id"],
            network_identifier=network["id"],
            action=RbacNetworkActions.SHARED,
        ),
    )

    # create default security group rules
    create_external_security_group_rules(
        conn, project_identifier=project["id"], security_group_identifier="default"
    )

    allocate_floating_ips(
        conn,
        network_identifier=external_network,
        project_identifier=project["id"],
        number_to_create=number_of_floating_ips,
    )


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
