from typing import Optional, List

from enums.network_providers import NetworkProviders
from enums.rbac_network_actions import RbacNetworkActions
from enums.user_domains import UserDomains

from openstack.connection import Connection

from openstack_api.openstack_network import (
    create_network,
    create_network_rbac,
    allocate_floating_ips,
)
from openstack_api.openstack_project import create_project
from openstack_api.openstack_router import create_router, add_interface_to_router
from openstack_api.openstack_security_groups import (
    refresh_security_groups,
    create_https_security_group,
    create_http_security_group,
    create_external_security_group_rules,
)
from openstack_api.openstack_roles import assign_role_to_user
from openstack_api.openstack_subnet import create_subnet
from structs.network_details import NetworkDetails
from structs.network_rbac import NetworkRbac

from structs.project_details import ProjectDetails
from structs.role_details import RoleDetails
from structs.router_details import RouterDetails


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
def create_external_project(
    conn: Connection,
    project_name: str,
    project_email: str,
    project_description: str,
    external_network_name: str,
    external_subnet_name: str,
    external_router_name: str,
    floating_ip_num: int = 1,
    project_immutable: Optional[bool] = None,
    parent_id: Optional[str] = None,
    admin_user_list: Optional[List[str]] = None,
    stfc_user_list: Optional[List[str]] = None,
):
    """
    create an external project
    :param conn: Openstack connection object
    :param project_name: A string for project name
    :param project_email: A string for email associated with the project
    :param project_description: A string for project description
    :param external_network_name: A string for external network name
    :param external_subnet_name: A string for external subnet name
    :param external_router_name: A string for external router name
    :param floating_ip_num: Number of floating ips to assign to project (default=1)
    :param project_immutable: (Optional) A boolean representing if project is immutable (True) or not (False)
    :param parent_id: (Optional) A string for parent project
    :param admin_user_list: (Optional) A list of strings to add as admins to the project
    :param stfc_user_list: (Optional) A list of strings to add as regular users (stfc domain)
    """
    if not admin_user_list:
        admin_user_list = []

    if not stfc_user_list:
        stfc_user_list = []

    project = create_project(
        conn,
        ProjectDetails(
            name=project_name,
            email=project_email,
            description=project_description,
            immutable=project_immutable,
            parent_id=parent_id,
        ),
    )

    network = create_network(
        conn,
        NetworkDetails(
            name=external_network_name,
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
            router_name=external_router_name,
            router_description="",
            project_identifier=project["id"],
            external_gateway="External",
            is_distributed=False,
        ),
    )

    subnet = create_subnet(
        conn,
        network_identifier=network["id"],
        subnet_name=external_subnet_name,
        subnet_description="",
        dhcp_enabled=True,
    )

    add_interface_to_router(
        conn,
        project_identifier=project["id"],
        router_identifier=router["id"],
        subnet_identifier=subnet["id"],
    )

    # wait for default security group
    refresh_security_groups(conn, project["id"])

    # create default security group rules
    create_external_security_group_rules(
        conn, project_identifier=project["id"], security_group_identifier="default"
    )
    create_http_security_group(conn, project_identifier=project["id"])
    create_https_security_group(conn, project_identifier=project["id"])

    create_network_rbac(
        conn,
        NetworkRbac(
            project_identifier=project["id"],
            network_identifier=network["id"],
            action=RbacNetworkActions.SHARED,
        ),
    )

    allocate_floating_ips(
        conn,
        network_identifier=network["id"],
        project_identifier=project["id"],
        number_to_create=floating_ip_num,
    )

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

    for stfc_user in stfc_user_list:
        assign_role_to_user(
            conn,
            RoleDetails(
                user_identifier=stfc_user,
                user_domain=UserDomains.STFC,
                project_identifier=project["id"],
                role_identifier="user",
            ),
        )
