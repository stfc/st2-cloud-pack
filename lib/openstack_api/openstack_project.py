from typing import List

from openstack.identity.v3.project import Project

from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_query import OpenstackQuery
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase


class OpenstackProject(OpenstackWrapperBase):
    # Lists all possible query presets for project.list
    SEARCH_QUERY_PRESETS: List[str] = [
        "all_projects",
        "projects_id_in",
        "projects_id_not_in",
        "projects_name_in",
        "projects_name_not_in",
        "projects_name_contains",
        "projects_name_not_contains",
    ]

    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(self._connection_cls)
        self._query_api = OpenstackQuery(self._connection_cls)

    def __getitem__(self, item):
        return getattr(self, item)

    def search_all_projects(self, cloud_account: str, **_) -> List[Project]:
        """
        Returns a list of projects matching a given query
        :param cloud_account: The associated clouds.yaml account
        :return: A list of all projects
        """

        with self._connection_cls(cloud_account) as conn:
            return conn.list_projects()

    def search_projects_name_in(
        self, cloud_account: str, names: List[str], **_
    ) -> List[Project]:
        """
        Returns a list of projects with names in the list given
        :param cloud_account: The associated clouds.yaml account
        :param names: List of names that should pass the query
        :return: A list of projects matching the query
        """
        selected_projects = self.search_all_projects(cloud_account)

        return self._query_api.apply_query(
            selected_projects, self._query_api.query_prop_in("name", names)
        )

    def search_projects_name_not_in(
        self, cloud_account: str, names: List[str], **_
    ) -> List[Project]:
        """
        Returns a list of projects with names that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param names: List of names that should not pass the query
        :return: A list of projects matching the query
        """
        selected_projects = self.search_all_projects(cloud_account)

        return self._query_api.apply_query(
            selected_projects,
            self._query_api.query_prop_not_in("name", names),
        )

    def search_projects_name_contains(
        self, cloud_account: str, name_snippets: List[str], **_
    ) -> List[Project]:
        """
        Returns a list of projects with names containing the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param name_snippets: List of name snippets that should be in the project names returned
        :return: A list of projects matching the query
        """
        selected_projects = self.search_all_projects(cloud_account)

        return self._query_api.apply_query(
            selected_projects,
            self._query_api.query_prop_contains("name", name_snippets),
        )

    def search_projects_name_not_contains(
        self, cloud_account: str, name_snippets: List[str], **_
    ) -> List[Project]:
        """
        Returns a list of projects with names that don't contain the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param name_snippets: List of name snippets that should not be in the project names returned
        :return: A list of projects matching the query
        """
        selected_projects = self.search_all_projects(cloud_account)

        return self._query_api.apply_query(
            selected_projects,
            self._query_api.query_prop_not_contains("name", name_snippets),
        )

    def search_projects_id_in(
        self, cloud_account: str, ids: List[str], **_
    ) -> List[Project]:
        """
        Returns a list of projects with ids in the list given
        :param cloud_account: The associated clouds.yaml account
        :param ids: List of ids that should pass the query
        :return: A list of projects matching the query
        """
        selected_fips = self.search_all_projects(cloud_account)

        return self._query_api.apply_query(
            selected_fips, self._query_api.query_prop_in("id", ids)
        )

    def search_projects_id_not_in(
        self, cloud_account: str, ids: List[str], **_
    ) -> List[Project]:
        """
        Returns a list of projects with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param ids: List of ids that should not pass the query
        :return: A list of projects matching the query
        """
        selected_fips = self.search_all_projects(cloud_account)

        return self._query_api.apply_query(
            selected_fips, self._query_api.query_prop_not_in("id", ids)
        )
