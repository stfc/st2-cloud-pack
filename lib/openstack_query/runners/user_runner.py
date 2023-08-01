from typing import Optional, Dict, List

from openstack.identity.v3.user import User
from openstack.exceptions import ResourceNotFound

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.query_runner import QueryRunner

from exceptions.parse_query_error import ParseQueryError

# pylint:disable=too-few-public-methods


class UserRunner(QueryRunner):
    """
    Runner class for openstack Server resource.
    ServerRunner encapsulates running any openstacksdk Server commands
    """

    STFC_DOMAIN_ID = "TEST"

    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[Dict[str, str]] = None,
    ) -> List[User]:
        """
        This method runs the query by running openstacksdk commands

        For UserQuery, this command gets all users by domain ID
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional set of filter kwargs to pass to conn.compute.servers()
            to limit number of users returned.


        """
        if not filter_kwargs:
            filter_kwargs = {}
        if "domain_id" not in filter_kwargs.keys():
            filter_kwargs.update({"domain_id": self.STFC_DOMAIN_ID})
        return list(conn.identity.v3.users(**filter_kwargs))

    def _parse_subset(self, _: OpenstackConnection, subset: List[User]) -> List[User]:
        """
        This method is a helper function that will check a list of users to ensure that they are valid Server
        objects
        :param subset: A list of openstack Server objects
        """
        if any(not isinstance(i, User) for i in subset):
            raise ParseQueryError("'from_subset' only accepts User openstack objects")
        return subset
