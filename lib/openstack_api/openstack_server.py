from typing import List

from openstack.compute.v2.server import Server

from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_query import OpenstackQuery
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase


class OpenstackServer(OpenstackWrapperBase):
    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(self._connection_cls)
        self._query_api = OpenstackQuery(self._connection_cls)

    def __getitem__(self, item):
        return getattr(self, item)

    # pylint:disable=unused-argument
    def search_all_servers(
        self, cloud_account: str, project_identifier: str, **kwargs
    ) -> List[Server]:
        """
        Returns a list of Servers matching a given query
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :return: A list of all servers
        """
        selected_servers = []
        if project_identifier == "":
            projects = self._identity_api.list_projects(cloud_account)
        else:
            projects = [
                self._identity_api.find_mandatory_project(
                    cloud_account, project_identifier=project_identifier
                )
            ]

        with self._connection_cls(cloud_account) as conn:
            for project in projects:
                selected_servers.extend(
                    conn.list_servers(
                        filters={
                            "all_tenants": True,
                            "project_id": project.id,
                            "limit": 10000,
                        }
                    )
                )
        return selected_servers

    # pylint:disable=unused-argument
    def search_servers_older_than(
        self, cloud_account: str, project_identifier: str, days: int, **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers older than a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days the servers should be older than
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers,
            lambda a: self._query_api.datetime_before_x_days(a["created_at"], days),
        )

    # pylint:disable=unused-argument
    def search_servers_younger_than(
        self, cloud_account: str, project_identifier: str, days: int, **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers older than a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days the servers should be older than
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers,
            lambda a: not self._query_api.datetime_before_x_days(a["created_at"], days),
        )

    # pylint:disable=unused-argument
    def search_servers_last_updated_before(
        self, cloud_account: str, project_identifier: str, days: int, **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers updated before a specified number of days in the past
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days before which the servers should have last been updated
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers,
            lambda a: self._query_api.datetime_before_x_days(a["updated_at"], days),
        )

    # pylint:disable=unused-argument
    def search_servers_last_updated_after(
        self, cloud_account: str, project_identifier: str, days: int, **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers updated after a specified number of days in the past
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days after which the servers should have last been updated
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers,
            lambda a: not self._query_api.datetime_before_x_days(a["updated_at"], days),
        )

    # pylint:disable=unused-argument
    def search_servers_name_in(
        self, cloud_account: str, project_identifier: str, names: List[str], **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers with names in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param names: List of names that should pass the query
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers, lambda a: a["name"] in names
        )

    # pylint:disable=unused-argument
    def search_servers_name_not_in(
        self, cloud_account: str, project_identifier: str, names: List[str], **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers with names that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param names: List of names that should not pass the query
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers, lambda a: not a["name"] in names
        )

    # pylint:disable=unused-argument
    def search_servers_name_contains(
        self,
        cloud_account: str,
        project_identifier: str,
        name_snippets: List[str],
        **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers with names containing the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param name_snippets: List of name snippets that should be in the server names returned
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers,
            lambda a: all(name_snippet in a["name"] for name_snippet in name_snippets),
        )

    # pylint:disable=unused-argument
    def search_servers_name_not_contains(
        self,
        cloud_account: str,
        project_identifier: str,
        name_snippets: List[str],
        **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers with names that don't contain the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param name_snippets: List of name snippets that should not be in the server names returned
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers,
            lambda a: all(
                name_snippet not in a["name"] for name_snippet in name_snippets
            ),
        )

    # pylint:disable=unused-argument
    def search_servers_id_in(
        self, cloud_account: str, project_identifier: str, ids: List[str], **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers with ids in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param ids: List of ids that should pass the query
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(selected_servers, lambda a: a["id"] in ids)

    # pylint:disable=unused-argument
    def search_servers_id_not_in(
        self, cloud_account: str, project_identifier: str, ids: List[str], **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param ids: List of v that should not pass the query
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers, lambda a: not a["id"] in ids
        )

    def search_servers_errored(
        self, cloud_account: str, project_identifier: str, **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param ids: List of v that should not pass the query
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers, lambda a: "ERROR" in a["status"]
        )

    def search_servers_shutoff(
        self, cloud_account: str, project_identifier: str, **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param ids: List of v that should not pass the query
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers, lambda a: "SHUTOFF" in a["status"]
        )

    def search_servers_errored_and_shutoff(
        self, cloud_account: str, project_identifier: str, **kwargs
    ) -> List[Server]:
        """
        Returns a list of servers with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param ids: List of v that should not pass the query
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers,
            lambda a: all(x in a["status"] for x in ["SHUTOFF", "ERRORED"]),
        )
