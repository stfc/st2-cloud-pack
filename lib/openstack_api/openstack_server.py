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

    def search_servers(
        self, cloud_account: str, project_identifier: str
    ) -> List[Server]:
        """
        Returns a list of Servers matching a given query
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :return: A list of all servers
        """
        selected_servers = []
        if project_identifier == "":
            projects = [
                self._identity_api.find_mandatory_project(
                    cloud_account, project_identifier=project_identifier
                )
            ]
        else:
            projects = self._identity_api.list_projects(cloud_account)

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

    def search_servers_older_than(
        self, cloud_account: str, project_identifier: str, days: int
    ) -> List[Server]:
        """
        Returns a list of servers older than a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days the servers should be older than
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return OpenstackQuery.apply_query(
            selected_servers,
            lambda a: OpenstackQuery.datetime_before_x_days(a["created_at"], days),
        )

    def search_servers_younger_than(
        self, cloud_account: str, project_identifier: str, days: int
    ) -> List[Server]:
        """
        Returns a list of servers older than a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days the servers should be older than
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return OpenstackQuery.apply_query(
            selected_servers,
            lambda a: not OpenstackQuery.datetime_before_x_days(a["created_at"], days),
        )

    def search_servers_updated_before(
        self, cloud_account: str, project_identifier: str, days: int
    ) -> List[Server]:
        """
        Returns a list of servers updated before a specified number of days in the past
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days before which the servers should have last been updated
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return OpenstackQuery.apply_query(
            selected_servers,
            lambda a: OpenstackQuery.datetime_before_x_days(a["updated_at"], days),
        )

    def search_servers_updated_after(
        self, cloud_account: str, project_identifier: str, days: int
    ) -> List[Server]:
        """
        Returns a list of servers updated befafterore a specified number of days in the past
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days after which the servers should have last been updated
        :return: A list of servers matching the query
        """
        selected_servers = self.search_servers(cloud_account, project_identifier)

        return OpenstackQuery.apply_query(
            selected_servers,
            lambda a: not OpenstackQuery.datetime_before_x_days(a["updated_at"], days),
        )
