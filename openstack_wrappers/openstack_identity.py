# TODO extract this to own class
from typing import Optional

from openstack.identity.v3.domain import Domain

from openstack_wrappers.openstack_connection import OpenstackConnection


class MissingMandatoryParamError(ValueError):
    pass


# pylint: disable=too-few-public-methods
class OpenstackIdentity:
    @staticmethod
    def find_domain(domain: str) -> Optional[Domain]:
        """
        Finds the given domain based on the UUID or name
        @param domain: (str) the UUID or name of the domain to find
        @return: The domain if found, else None
        """

        if not domain:
            raise MissingMandatoryParamError("No project or domain were provided")

        with OpenstackConnection() as conn:
            return conn.identity.find_domain(name_or_id=domain, ignore_missing=True)
