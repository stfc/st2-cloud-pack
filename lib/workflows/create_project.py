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
    if project_domain != "default":
        raise RuntimeError(
            "domain support is work in progress, please use default domain",
        )
    return (
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
        if networking_type == "external"
        else create_internal_project(
            conn=conn,
            project_name=f"{project_name}",
            project_email=project_email,
            project_description=project_description,
            project_immutable=project_immutable,
            parent_id=parent_id,
            admin_user_list=admin_user_list,
            stfc_user_list=user_list,
        )
    )
