from openstack.connection import Connection

from apis.openstack_api.enums.user_domains import UserDomains
from apis.openstack_api.openstack_roles import (
    assign_role_to_user,
    remove_role_from_user,
)
from apis.openstack_api.structs.role_details import RoleDetails


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
    assign_role_to_user(conn, details=details)
    return True  # the above method always returns None


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
    remove_role_from_user(conn, details=details)
    return True
