from typing import Tuple
from openstack.connection import Connection

from openstack.identity.v3.project import Project
from openstack.identity.v3.role import Role
from openstack.identity.v3.user import User

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from structs.role_details import RoleDetails


def assign_group_role_to_project(conn: Connection, project, role, group) -> None:
    """
    Assigns a given role to the specified group
    :param conn: openstack connection object
    :param project: The project name or ID to assign the role to
    :param role: The role name or ID to assign
    :param group: The group name or ID to assign the role to
    """
    # This is run rarely in comparison to most actions, as it
    # likely gets ran once or twice per new project
    # Assume the user has already checked the group exists and has stripped it
    role = conn.identity.find_role(role, ignore_missing=False)
    project = conn.identity.find_project(project, ignore_missing=False)
    group = conn.identity.find_group(group, ignore_missing=False)

    conn.identity.assign_project_role_to_group(project=project, group=group, role=role)


def assign_role_to_user(conn: Connection, details: RoleDetails) -> None:
    """
    Assigns a given role to the specified user
    :param conn: openstack connection object
    :param details: The details to find the role with
    """
    user, project, role = _find_role_details(conn, details)
    conn.identity.assign_project_role_to_user(project=project, user=user, role=role)


def remove_role_from_user(conn: Connection, details: RoleDetails) -> None:
    """
    Assigns a given role to the specified user
    :param conn: openstack connection object
    :param details: The details to find the role with
    """
    user, project, role = _find_role_details(conn, details)
    conn.identity.unassign_project_role_from_user(project=project, user=user, role=role)


def _find_role_details(
    conn: Connection, details: RoleDetails
) -> Tuple[User, Project, Role]:
    """
    :param conn: openstack connection object
    :param details: The details to find the role with
    Finds the various OS objects required for role manipulation
    """
    details.project_identifier = details.project_identifier.strip()
    if not details.project_identifier:
        raise MissingMandatoryParamError("The project name is missing")

    details.role_identifier = details.role_identifier.strip()
    if not details.role_identifier:
        raise MissingMandatoryParamError("The role name is missing")

    details.user_identifier = details.user_identifier.strip()
    if not details.user_identifier:
        raise MissingMandatoryParamError("A user name or ID must be provided")

    domain = details.user_domain.name.lower().strip()

    project = conn.identity.find_project(
        details.project_identifier, ignore_missing=False
    )
    domain_id = conn.identity.find_domain(domain, ignore_missing=False)
    user = conn.identity.find_user(
        details.user_identifier, domain_id=domain_id.id, ignore_missing=False
    )
    role = conn.identity.find_role(details.role_identifier, ignore_missing=False)
    return user, project, role
