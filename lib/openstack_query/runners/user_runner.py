from typing import Optional, Dict, List

from openstack.identity.v3.user import User

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.query_runner import QueryRunner

from exceptions.parse_query_error import ParseQueryError
from exceptions.enum_mapping_error import EnumMappingError

# pylint:disable=too-few-public-methods
from enums.user_domains import UserDomains


class UserRunner(QueryRunner):
    """
    Runner class for openstack Server resource.
    ServerRunner encapsulates running any openstacksdk Server commands
    """

    DEFAULT_DOMAIN_ID = UserDomains.STFC

    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[Dict[str, str]] = None,
        from_domain: Optional[UserDomains] = None,
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
        if from_domain and "domain_id" in filter_kwargs.keys():
            raise ParseQueryError(
                "This query uses a preset that requires searching on domain_ids "
                "- but you've provided a domain using from_domain "
                "- please use one or the other not both"
            )
        if from_domain:
            domain_id = self._get_user_domain(conn, from_domain)
        else:
            domain_id = self._get_user_domain(conn, self.DEFAULT_DOMAIN_ID)

        filter_kwargs.update({"domain_id": domain_id})

        return list(conn.identity.users(**filter_kwargs))

    def _get_user_domain(
        self, conn: OpenstackConnection, user_domain: UserDomains
    ) -> str:
        """
        Gets user domain string from UserDomains enum
        """
        try:
            return {
                UserDomains.DEFAULT: conn.identity.find_domain("default"),
                UserDomains.STFC: conn.identity.find_domain("stfc"),
                UserDomains.OPENID: conn.identity.find_domain(
                    "openid"
                ),  # irisiam domain became openid since Stein
            }[user_domain]["id"]
        except KeyError as exp:
            raise EnumMappingError(
                f"Mapping for domain {user_domain.name} not found"
            ) from exp

    def _parse_subset(self, _: OpenstackConnection, subset: List[User]) -> List[User]:
        """
        This method is a helper function that will check a list of users to ensure that they are valid Server
        objects
        :param subset: A list of openstack Server objects
        """
        if any(not isinstance(i, User) for i in subset):
            raise ParseQueryError("'from_subset' only accepts User openstack objects")
        return subset
