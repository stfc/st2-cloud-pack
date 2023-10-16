import logging
from typing import Optional, Dict, List

from openstack.identity.v3.user import User

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.runner_wrapper import RunnerWrapper

from exceptions.parse_query_error import ParseQueryError
from exceptions.enum_mapping_error import EnumMappingError

from enums.query.props.user_properties import UserProperties
from enums.user_domains import UserDomains

logger = logging.getLogger(__name__)

# pylint:disable=too-few-public-methods


class UserRunner(RunnerWrapper):
    """
    Runner class for openstack User resource.
    UserRunner encapsulates running any openstacksdk User commands
    """

    DEFAULT_DOMAIN = UserDomains.STFC
    RESOURCE_TYPE = User

    @staticmethod
    def _get_marker(obj: User) -> str:
        """
        This method returns the marker value for a User object, required for pagination
        :param obj: An Server object to get the marker property for
        """
        return UserProperties.get_prop_mapping("id")(obj)

    def _parse_meta_params(
        self, conn: OpenstackConnection, from_domain: Optional[UserDomains] = None
    ) -> Dict:
        """
        This method is a helper function that will parse a set of query meta params related to openstack user queries
        :param conn: An OpenstackConnection object - used to connect to openstack and parse meta params
        """
        if from_domain:
            logger.info("searching in given user domain: '%s'", from_domain.name)
            return {"domain_id": self._get_user_domain(conn, from_domain)}
        return {}

    def _get_user_domain(
        self, conn: OpenstackConnection, user_domain: UserDomains
    ) -> str:
        """
        Helper function to get user domain id from a given UserDomains enum
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param user_domain: An enum that represents possible user domains
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

    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[Dict[str, str]] = None,
        **meta_params,
    ) -> List[Optional[User]]:
        """
        This method runs the query by running openstacksdk commands

        For UserQuery, this command gets all users by domain ID
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional list of filter kwargs to pass to conn.identity.users()
        """

        if not filter_kwargs:
            filter_kwargs = {}

        # having a filter of 'id' - will automatically mean no other filter kwargs
        selected_id = filter_kwargs.get("id", None)
        if selected_id:
            val = conn.identity.find_user(selected_id, ignore_missing=True)
            return [val] if val else []

        if "domain_id" in meta_params and "domain_id" in filter_kwargs.keys():
            raise ParseQueryError(
                "This query uses a preset that requires searching on domain_ids "
                "- but you've provided a domain using from_domain "
                "- please use one or the other not both"
            )

        filter_kwargs.update(
            {"domain_id": self._get_user_domain(conn, self.DEFAULT_DOMAIN)}
        )

        if "domain_id" in meta_params and meta_params["domain_id"]:
            filter_kwargs.update({"domain_id": meta_params["domain_id"]})
        else:
            logger.info(
                "no domain_id given, will use id for default user domain: '%s'",
                self.DEFAULT_DOMAIN.name,
            )

        logger.debug(
            "searching for users using domain_id: '%s'", filter_kwargs["domain_id"]
        )
        logger.debug(
            "running paginated openstacksdk command conn.identity.users (%s)",
            ",".join(f"{key}={value}" for key, value in filter_kwargs.items()),
        )
        return self._run_paginated_query(conn.identity.users, filter_kwargs)
