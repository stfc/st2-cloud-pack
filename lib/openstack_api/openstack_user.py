from typing import Optional
from openstack.connection import Connection

from openstack.identity.v3.user import User

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from enums.user_domains import UserDomains


def find_user(
    conn: Connection, user_identifier: str, user_domain: UserDomains
) -> Optional[User]:
    """
    Finds a user with the given name or ID
    :param conn: openstack connection object
    :param user_identifier: The name or Openstack ID for the user
    :param user_domain: The domain to search for the user in
    :return: The found user, or None
    """
    user_identifier = user_identifier.strip()
    if not user_identifier:
        raise MissingMandatoryParamError("A user name or ID must be provided")
    domain = user_domain.value.lower().strip()

    domain_id = conn.identity.find_domain(domain, ignore_missing=False)
    result = conn.identity.find_user(
        user_identifier, domain_id=domain_id.id, ignore_missing=True
    )
    return result
