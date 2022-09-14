from typing import List

from openstack.compute.v2.hypervisor import Hypervisor

from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_query import OpenstackQuery
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase


class OpenstackHypervisor(OpenstackWrapperBase):
    # Lists all possible query presets for hypervisor.list
    SEARCH_QUERY_PRESETS: List[str] = [
        "all_hvs",
        "hvs_id_in",
        "hvs_id_not_in",
        "hvs_name_in",
        "hvs_name_not_in",
        "hvs_name_contains",
        "hvs_name_not_contains",
        "hvs_down",
        "hvs_up",
        "hvs_disabled",
        "hvs_enabled",
    ]

    # Queries to be used for OpenstackQuery
    def _query_down(self, hypervisor: Hypervisor):
        """
        Returns whether a hypervisor is down
        """
        return "down" in hypervisor["state"]

    def _query_up(self, hypervisor: Hypervisor):
        """
        Returns whether a hypervisor is up
        """
        return "up" in hypervisor["state"]

    def _query_disabled(self, hypervisor: Hypervisor):
        """
        Returns whether a hypervisor is disabled
        """
        return "disabled" in hypervisor["status"]

    def _query_enabled(self, hypervisor: Hypervisor):
        """
        Returns whether a hypervisor is enabled
        """
        return "enabled" in hypervisor["status"]

    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._query_api = OpenstackQuery(self._connection_cls)

    def __getitem__(self, item):
        return getattr(self, item)

    def search_all_hvs(self, cloud_account: str, **_) -> List[Hypervisor]:
        """
        Returns a list of hvs matching a given query
        :param cloud_account: The associated clouds.yaml account
        :return: A list of all hvs
        """

        with self._connection_cls(cloud_account) as conn:
            return conn.list_hypervisors(filters={})

    def search_hvs_name_in(
        self, cloud_account: str, names: List[str], **_
    ) -> List[Hypervisor]:
        """
        Returns a list of hvs with names in the list given
        :param cloud_account: The associated clouds.yaml account
        :param names: List of names that should pass the query
        :return: A list of hvs matching the query
        """
        selected_hvs = self.search_all_hvs(cloud_account)

        return self._query_api.apply_query(
            selected_hvs, self._query_api.query_prop_in("name", names)
        )

    def search_hvs_name_not_in(
        self, cloud_account: str, names: List[str], **_
    ) -> List[Hypervisor]:
        """
        Returns a list of hvs with names that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param names: List of names that should not pass the query
        :return: A list of hvs matching the query
        """
        selected_hvs = self.search_all_hvs(cloud_account)

        return self._query_api.apply_query(
            selected_hvs, self._query_api.query_prop_not_in("name", names)
        )

    def search_hvs_name_contains(
        self, cloud_account: str, name_snippets: List[str], **_
    ) -> List[Hypervisor]:
        """
        Returns a list of hvs with names containing the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param name_snippets: List of name snippets that should be in the hypervisor names returned
        :return: A list of hvs matching the query
        """
        selected_hvs = self.search_all_hvs(cloud_account)

        return self._query_api.apply_query(
            selected_hvs,
            self._query_api.query_prop_contains("name", name_snippets),
        )

    def search_hvs_name_not_contains(
        self, cloud_account: str, name_snippets: List[str], **_
    ) -> List[Hypervisor]:
        """
        Returns a list of hvs with names that don't contain the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param name_snippets: List of name snippets that should not be in the hypervisor names returned
        :return: A list of hvs matching the query
        """
        selected_hvs = self.search_all_hvs(cloud_account)

        return self._query_api.apply_query(
            selected_hvs,
            self._query_api.query_prop_not_contains("name", name_snippets),
        )

    def search_hvs_id_in(
        self, cloud_account: str, ids: List[str], **_
    ) -> List[Hypervisor]:
        """
        Returns a list of hvs with ids in the list given
        :param cloud_account: The associated clouds.yaml account
        :param ids: List of ids that should pass the query
        :return: A list of hvs matching the query
        """
        selected_hvs = self.search_all_hvs(cloud_account)

        return self._query_api.apply_query(
            selected_hvs,
            self._query_api.query_prop_in("id", ids),
        )

    def search_hvs_id_not_in(
        self, cloud_account: str, ids: List[str], **_
    ) -> List[Hypervisor]:
        """
        Returns a list of hvs with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param ids: List of ids that should not pass the query
        :return: A list of hvs matching the query
        """
        selected_hvs = self.search_all_hvs(cloud_account)

        return self._query_api.apply_query(
            selected_hvs, self._query_api.query_prop_not_in("id", ids)
        )

    def search_hvs_down(self, cloud_account: str, **_) -> List[Hypervisor]:
        """
        Returns a list of hvs that are down
        :param cloud_account: The associated clouds.yaml account
        :return: A list of hvs matching the query
        """
        selected_hvs = self.search_all_hvs(cloud_account)

        return self._query_api.apply_query(selected_hvs, self._query_down)

    def search_hvs_up(self, cloud_account: str, **_) -> List[Hypervisor]:
        """
        Returns a list of hvs that are up
        :param cloud_account: The associated clouds.yaml account
        :return: A list of hvs matching the query
        """
        selected_hvs = self.search_all_hvs(cloud_account)

        return self._query_api.apply_query(selected_hvs, self._query_up)

    def search_hvs_disabled(self, cloud_account: str, **_) -> List[Hypervisor]:
        """
        Returns a list of hvs that are disabled
        :param cloud_account: The associated clouds.yaml account
        :return: A list of hvs matching the query
        """
        selected_hvs = self.search_all_hvs(cloud_account)

        return self._query_api.apply_query(selected_hvs, self._query_disabled)

    def search_hvs_enabled(self, cloud_account: str, **_) -> List[Hypervisor]:
        """
        Returns a list of hvs that are enabled
        :param cloud_account: The associated clouds.yaml account
        :return: A list of hvs matching the query
        """
        selected_hvs = self.search_all_hvs(cloud_account)

        return self._query_api.apply_query(selected_hvs, self._query_enabled)
