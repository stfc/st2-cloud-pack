from openstack.connection import Connection

from enums.user_domains import UserDomains
from openstack_api import openstack_roles
from openstack_api.openstack_roles import assign_group_role_to_project
from structs.role_details import RoleDetails


def role_add(
    conn: Connection,
    user_identifier: str,
    project_identifier: str,
    role_identifier: str,
    user_domain: str,
) -> bool:
    """
    Add a given user a project role
    :param conn: Openstack connection object
    :param user_identifier: Name or ID of the user to assign a role to
    :param project_identifier: Name or ID of the project this applies to
    :param role_identifier: Name or ID of the role to assign
    :param user_domain: The domain the user is associated with
    :return: status
    """
    details = RoleDetails(
        user_identifier=user_identifier,
        project_identifier=project_identifier,
        role_identifier=role_identifier,
        user_domain=UserDomains.from_string(user_domain),
    )
    openstack_roles.assign_role_to_user(conn, details=details)
    return True  # the above method always returns None


def role_assign_group(
    conn: Connection,
    project_identifier: str,
    role_identifier: str,
    group_name: str,
) -> bool:
    """
    Assigns a pre-created group to map the specified role to members of that
    group into a project.
    :param conn: Openstack connection object
    :param project_identifier: Name or ID of the project to assign to
    :param role_identifier: Name or ID of the role to assign
    :param group_name: Name of the group to assign the user to
    :return: True always
    """
    assign_group_role_to_project(
        conn, project=project_identifier, role=role_identifier, group=group_name
    )
    return True


def add_user_to_group(
    conn: Connection,
    user_identifier: str,
    user_domain: str,
    group_name: str,
    group_domain: str,
) -> bool:
    """
    Assigns a user to an existing group
    :param conn: Openstack connection object
    :param user_identifier: Name or ID of the user to assign to the group
    :param user_domain: The domain the user is associated with
    :param group_name: Name of the group to assign the user to
    :param group_domain: The domain the group is associated with
    :return: True always
    """
    openstack_roles.add_user_to_group(
        conn,
        user_identifier=user_identifier,
        user_domain=user_domain,
        group_name=group_name,
        group_domain=group_domain,
    )
    return True


def role_remove(
    conn: Connection,
    user_identifier: str,
    project_identifier: str,
    role_identifier: str,
    user_domain: str,
) -> bool:
    """
    Removes a project role from a given user
    :param conn: Openstack connection object
    :param user_identifier: Name or ID of the user to remove a role from
    :param project_identifier: Name or ID of the project this applies to
    :param role_identifier: Name or ID of the role to remove
    :param user_domain: The domain the user is associated with
    :return: status
    """
    details = RoleDetails(
        user_identifier=user_identifier,
        project_identifier=project_identifier,
        role_identifier=role_identifier,
        user_domain=UserDomains.from_string(user_domain),
    )
    openstack_roles.remove_role_from_user(conn, details=details)
    return True
