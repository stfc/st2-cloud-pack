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
from openstack_api.openstack_quota import set_quota
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
from structs.quota_details import QuotaDetails
from structs.role_details import RoleDetails
from structs.router_details import RouterDetails


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
def create_jasmin_external_project(
    conn: Connection,
    project_name: str,
    project_email: str,
    project_description: str,
    network_name: str,
    subnet_name: str,
    router_name: str,
    number_of_floating_ips: int = 1,
    number_of_security_group_rules: int = 200,
    project_immutable: Optional[bool] = None,
    parent_id: Optional[str] = None,
    admin_user_list: Optional[List[str]] = None,
    jasmin_user_list: Optional[List[str]] = None,
):
    """
    Create an external project for Jasmin tenants. This is a copy of
    create_external_project as a starting point to make changes for their specific
    requirements. This gives us certainty we're not affecting our existing code.
    In the future we will consolidate the common parts of the two...
    :param conn: Openstack connection object
    :param project_name: A string for project name
    :param project_email: A string for email associated with the project
    :param project_domain: Domain to create project in (to be added to project)
    :param project_description: A string for project description
    :param network_name: A string for external network name
    :param subnet_name: A string for external subnet name
    :param router_name: A string for external router name
    :param number_of_floating_ips: Number of floating ips to assign to project (default=1)
    :param number_of_security_group_rules: Quota for the no. of security group rules to assign (default=200)
    :param project_immutable: (Optional) A boolean representing if project is immutable (True) or not (False)
    :param parent_id: (Optional) A string for parent project
    :param admin_user_list: (Optional) A list of strings to add as admins to the project
    :param jasmin_user_list: A list of strings to add as regular users (jasmin domain)
    """

    admin_user_list = admin_user_list or []
    jasmin_user_list = jasmin_user_list or []

    # TODO Add project domain in future PR
    project = create_project(
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

    network = create_network(
        conn,
        NetworkDetails(
            name=network_name,
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
            router_name=router_name,
            router_description="",
            project_identifier=project["id"],
            external_gateway="JASMIN External Cloud Network",
            is_distributed=False,
        ),
    )

    subnet = create_subnet(
        conn,
        network_identifier=network["id"],
        subnet_name=subnet_name,
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

    set_quota(
        conn,
        QuotaDetails(
            project_identifier=project["id"],
            num_floating_ips=number_of_floating_ips,
            num_security_group_rules=number_of_security_group_rules,
        ),
    )
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
        network_identifier="JASMIN External Cloud Network",
        project_identifier=project["id"],
        number_to_create=number_of_floating_ips,
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

    for jasmin_user in jasmin_user_list:
        assign_role_to_user(
            conn,
            RoleDetails(
                user_identifier=jasmin_user,
                user_domain=UserDomains.JASMIN,
                project_identifier=project["id"],
                role_identifier="user",
            ),
        )
