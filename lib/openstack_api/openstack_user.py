from typing import List, Callable, Any, Dict

from openstack.identity.v3.user import User

from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_query import OpenstackQuery
from openstack_api.openstack_query_base import OpenstackQueryBase


class OpenstackUser(OpenstackQueryBase):
    # Lists all possible query presets for user.list
    SEARCH_QUERY_PRESETS: List[str] = [
        "all_users",
        "users_id_in",
        "users_id_not_in",
        "users_name_in",
        "users_name_not_in",
        "users_name_contains",
        "users_name_not_contains",
    ]

    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(self._connection_cls)
        self._query_api = OpenstackQuery(self._connection_cls)

    def get_query_property_funcs(self, _) -> Dict[str, Callable[[Any], Any]]:
        """
        Returns property functions for use with OpenstackQuery.parse_properties
        :param cloud_account: The associated clouds.yaml account
        """
        return {}

    def search_all_users(self, cloud_account: str, user_domain: str, **_) -> List[User]:
        """
        Returns a list of users matching a given query
        :param cloud_account: The associated clouds.yaml account
        :param user_domain: The user domain to get users from
        :return: A list of all users
        """
        filters = {"domain_id": user_domain}

        with self._connection_cls(cloud_account) as conn:
            return conn.list_users(**filters)

    def search_users_name_in(
        self, cloud_account: str, user_domain: str, names: List[str], **_
    ) -> List[User]:
        """
        Returns a list of users with names in the list given
        :param cloud_account: The associated clouds.yaml account
        :param user_domain: The user domain to get users from
        :param names: List of names that should pass the query
        :return: A list of users matching the query
        """
        selected_users = self.search_all_users(cloud_account, user_domain)

        return self._query_api.apply_query(
            selected_users, self._query_api.query_prop_in("name", names)
        )

    def search_users_name_not_in(
        self, cloud_account: str, user_domain: str, names: List[str], **_
    ) -> List[User]:
        """
        Returns a list of users with names that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param user_domain: The user domain to get users from
        :param names: List of names that should not pass the query
        :return: A list of users matching the query
        """
        selected_users = self.search_all_users(cloud_account, user_domain)

        return self._query_api.apply_query(
            selected_users,
            self._query_api.query_prop_not_in("name", names),
        )

    def search_users_name_contains(
        self, cloud_account: str, user_domain: str, name_snippets: List[str], **_
    ) -> List[User]:
        """
        Returns a list of users with names containing the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param user_domain: The user domain to get users from
        :param name_snippets: List of name snippets that should be in the user names returned
        :return: A list of users matching the query
        """
        selected_users = self.search_all_users(cloud_account, user_domain)

        return self._query_api.apply_query(
            selected_users,
            self._query_api.query_prop_contains("name", name_snippets),
        )

    def search_users_name_not_contains(
        self, cloud_account: str, user_domain: str, name_snippets: List[str], **_
    ) -> List[User]:
        """
        Returns a list of users with names that don't contain the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param user_domain: The user domain to get users from
        :param name_snippets: List of name snippets that should not be in the user names returned
        :return: A list of users matching the query
        """
        selected_users = self.search_all_users(cloud_account, user_domain)

        return self._query_api.apply_query(
            selected_users,
            self._query_api.query_prop_not_contains("name", name_snippets),
        )

    def search_users_id_in(
        self, cloud_account: str, user_domain: str, ids: List[str], **_
    ) -> List[User]:
        """
        Returns a list of users with ids in the list given
        :param cloud_account: The associated clouds.yaml account
        :param user_domain: The user domain to get users from
        :param ids: List of ids that should pass the query
        :return: A list of users matching the query
        """
        selected_users = self.search_all_users(cloud_account, user_domain)

        return self._query_api.apply_query(
            selected_users, self._query_api.query_prop_in("id", ids)
        )

    def search_users_id_not_in(
        self, cloud_account: str, user_domain: str, ids: List[str], **_
    ) -> List[User]:
        """
        Returns a list of users with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param user_domain: The user domain to get users from
        :param ids: List of ids that should not pass the query
        :return: A list of users matching the query
        """
        selected_users = self.search_all_users(cloud_account, user_domain)

        return self._query_api.apply_query(
            selected_users, self._query_api.query_prop_not_in("id", ids)
        )
