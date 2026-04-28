import re
from openstack.exceptions import ConflictException


def create_group(conn, group_name):
    """
    Creates a new users group
    :param conn: openstack connection object
    :param group_name: the name of the new users group
    :return: a group object
    """
    if not re.match(r"^[a-z0-9-]+$", group_name):
        raise ValueError(
            f"Group name '{group_name}' contains invalid characters. "
            "Only lowercase letters, numbers, and dashes are allowed."
        )

    try:
        return conn.identity.create_group(group_name)
    except ConflictException as err:
        # Strip out frames that are noise by rethrowing
        raise ConflictException(err.message) from err
