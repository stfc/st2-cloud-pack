from typing import List, Optional
from openstack.connection import Connection

from workflows.create_external_project import create_external_project
from workflows.create_internal_project import create_internal_project


def create_project(
    conn: Connection,
    project_name: str,
    project_email: str,
    project_description: str,
    project_domain: str,
    networking_type: str,
    number_of_floating_ips: int = 1,
    number_of_security_group_rules: int = 200,
    project_immutable: Optional[bool] = False,
    parent_id: Optional[str] = None,
    admin_user_list: Optional[List[str]] = None,
    user_list: Optional[List[str]] = None,
):
    """
    Create openstack project

    :param conn: Openstack Connection
    :type conn: Connection
    :param project_name: Project name
    :type project_name: str
    :param project_email: Contact email for project
    :type project_email: str
    :param project_description: Project Description
    :type project_description: str
    :param project_domain: Project domain
    :type project_domain: str
    :param networking_type: Project networking type, e.g. Internal, External
    :type networking_type: str
    :param number_of_floating_ips: Floating IP quota for project
    :type number_of_floating_ips: int
    :param number_of_security_group_rules: Security Group quota for project
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

    if project_domain != "default":
        raise NotImplementedError(
            "domain support is work in progress, please use default domain",
        )

    if networking_type == "internal":
        create_internal_project(
            conn=conn,
            project_name=f"{project_name}",
            project_email=project_email,
            project_description=project_description,
            project_immutable=project_immutable,
            parent_id=parent_id,
            admin_user_list=admin_user_list,
            stfc_user_list=user_list,
        )
    elif networking_type in ("external", "jasmin"):
        create_external_project(
            conn=conn,
            project_name=f"{project_name}",
            project_email=project_email,
            project_description=project_description,
            network_name=f"{project_name}-network",
            subnet_name=f"{project_name}-subnet",
            router_name=f"{project_name}-router",
            number_of_floating_ips=number_of_floating_ips,
            number_of_security_group_rules=number_of_security_group_rules,
            project_immutable=project_immutable,
            parent_id=parent_id,
            admin_user_list=admin_user_list,
            stfc_user_list=user_list,
        )
    else:
        raise NotImplementedError(f"Unknown networking type {networking_type}")
