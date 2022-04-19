from typing import Optional

from openstack.identity.v3.domain import Domain

from missing_mandatory_param_error import (
    MissingMandatoryParamError,
)
from openstack_connection import OpenstackConnection


# pylint: disable=too-few-public-methods
class OpenstackIdentity:
    @staticmethod
    def find_domain(cloud_account: str, domain: str) -> Optional[Domain]:
        """
        Finds the given domain based on the UUID or name
        @param cloud_account: The clouds.yaml account to use whilst connecting
        @param domain: (str) the UUID or name of the domain to find
        @return: The domain if found, else None
        """

        if not domain:
            raise MissingMandatoryParamError("No project or domain were provided")

        with OpenstackConnection(cloud_account) as conn:
            return conn.identity.find_domain(name_or_id=domain, ignore_missing=True)
