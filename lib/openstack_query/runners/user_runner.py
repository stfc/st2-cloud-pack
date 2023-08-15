import logging
from typing import Optional, Dict, List

from openstack.identity.v3.user import User

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.query_runner import QueryRunner

from exceptions.parse_query_error import ParseQueryError
from exceptions.enum_mapping_error import EnumMappingError

from enums.user_domains import UserDomains

logger = logging.getLogger(__name__)

# pylint:disable=too-few-public-methods


class UserRunner(QueryRunner):
    """
    Runner class for openstack Server resource.
    ServerRunner encapsulates running any openstacksdk Server commands
    """

    DEFAULT_DOMAIN = UserDomains.STFC

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
            logger.info("searching in given user domain: '%s'", from_domain.name)
        else:
            domain_id = self._get_user_domain(conn, self.DEFAULT_DOMAIN)
            logger.info(
                "no domain_id given, will use id for default user domain: '%s'",
                self.DEFAULT_DOMAIN.name,
            )

        logger.debug("searching for users using domain_id: '%s'", domain_id)
        filter_kwargs.update({"domain_id": domain_id})

        logger.debug(
            "running openstacksdk command conn.identity.users (%s)",
            ",".join(f"{key}={value}" for key, value in filter_kwargs.items()),
        )
        return list(conn.identity.users(**filter_kwargs))

    def _get_user_domain(
        self, conn: OpenstackConnection, user_domain: UserDomains
    ) -> str:
        """
        Gets user domain string from UserDomains enum
        :param conn: openstack connection object used to get domain id
        :param user_domain: an enum representing the domain to search for users in
        """
        # get user domain name from enum
        domain_name_arg = {
            UserDomains.DEFAULT: "default",
            UserDomains.STFC: "stfc",
            UserDomains.OPENID: "openid",  # irisiam domain became openid since Stein
        }.get(user_domain, None)
        if not domain_name_arg:
            logging.error(
                "Error: No function mapping found for UserDomain %s "
                "- if you are here as a developer, you must add a mapping to an openstacksdk call "
                "to get domain_id for the enum",
                user_domain.name,
            )
            raise EnumMappingError(f"Mapping for domain {user_domain.name} not found")

        logger.debug(
            "running openstacksdk command conn.identity.find_domain(%s) to get domain",
            domain_name_arg,
        )
        return conn.identity.find_domain(domain_name_arg)

    def _parse_subset(self, _: OpenstackConnection, subset: List[User]) -> List[User]:
        """
        This method is a helper function that will check a list of users to ensure that they are valid Server
        objects
        :param subset: A list of openstack Server objects
        """
        if any(not isinstance(i, User) for i in subset):
            raise ParseQueryError("'from_subset' only accepts User openstack objects")
        return subset
