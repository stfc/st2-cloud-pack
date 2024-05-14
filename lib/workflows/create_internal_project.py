from typing import Optional, List

from enums.rbac_network_actions import RbacNetworkActions
from enums.user_domains import UserDomains

from openstack.connection import Connection

from openstack_api.openstack_network import create_network_rbac
from openstack_api.openstack_project import create_project
from openstack_api.openstack_security_groups import (
    refresh_security_groups,
    create_https_security_group,
    create_http_security_group,
    create_internal_security_group_rules,
)
from openstack_api.openstack_roles import assign_role_to_user

from structs.network_rbac import NetworkRbac
from structs.project_details import ProjectDetails
from structs.role_details import RoleDetails


# pylint: disable=too-many-arguments
def create_internal_project(
    conn: Connection,
    project_name: str,
    project_email: str,
    project_description: str,
    project_immutable: Optional[bool] = None,
    parent_id: Optional[str] = None,
    admin_user_list: Optional[List[str]] = None,
    stfc_user_list: Optional[List[str]] = None,
):
    """
    create an internal project
    :param conn: Openstack Connection object
    :param project_name: A string for project name
    :param project_email: A string for email associated with the project
    :param project_description: A string for project description
    :param project_immutable: A boolean representing if project is immutable (True) or not (False)
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

    # wait for default security group
    refresh_security_groups(conn, project["id"])

    create_internal_security_group_rules(conn, project["id"], "default")
    create_http_security_group(conn, project_identifier=project["id"])
    create_https_security_group(conn, project_identifier=project["id"])

    create_network_rbac(
        conn,
        NetworkRbac(
            project_identifier=project["id"],
            network_identifier="Internal",
            action=RbacNetworkActions.SHARED,
        ),
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
