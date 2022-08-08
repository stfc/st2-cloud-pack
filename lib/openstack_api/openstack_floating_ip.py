from typing import List

from openstack.network.v2.floating_ip import FloatingIP
from openstack.exceptions import HttpException

from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_query import OpenstackQuery
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase


class OpenstackFloatingIP(OpenstackWrapperBase):
    # Lists all possible query presets for floating.ip.list
    SEARCH_QUERY_PRESETS: List[str] = [
        "all_fips",
        "fips_older_than",
        "fips_younger_than",
        "fips_last_updated_before",
        "fips_last_updated_after",
        "fips_id_in",
        "fips_id_not_in",
        "fips_name_in",
        "fips_name_not_in",
        "fips_name_contains",
        "fips_name_not_contains",
        "fips_down",
    ]

    # Lists possible queries presets that don't require a project to function
    SEARCH_QUERY_PRESETS_NO_PROJECT: List[str] = [
        "fips_older_than",
        "fips_last_updated_before",
        "fips_down",
    ]

    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(self._connection_cls)
        self._query_api = OpenstackQuery(self._connection_cls)

    def __getitem__(self, item):
        return getattr(self, item)

    def search_all_fips(
        self, cloud_account: str, project_identifier: str, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips matching a given query
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :return: A list of all floating ips
        """
        selected_fips = []
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
                try:
                    selected_fips.extend(
                        conn.list_floating_ips(
                            filters={
                                "all_tenants": True,
                                "project_id": project.id,
                                "limit": 10000,
                            }
                        )
                    )
                except HttpException as err:
                    print(
                        f"Failed to list floating ips in the project with id {project.id}"
                    )
                    print(err)
        return selected_fips

    def search_fips_older_than(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips older than a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param days: The number of days the floating ips should be older than
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            lambda a: self._query_api.datetime_before_x_days(a["created_at"], days),
        )

    def search_fips_younger_than(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips older than a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param days: The number of days the floating ips should be older than
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            lambda a: not self._query_api.datetime_before_x_days(a["created_at"], days),
        )

    def search_fips_last_updated_before(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips updated before a specified number of days in the past
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param days: The number of days before which the floating ips should have last been updated
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            lambda a: self._query_api.datetime_before_x_days(a["updated_at"], days),
        )

    def search_fips_last_updated_after(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips updated after a specified number of days in the past
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param days: The number of days after which the floating ips should have last been updated
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            lambda a: not self._query_api.datetime_before_x_days(a["updated_at"], days),
        )

    def search_fips_name_in(
        self, cloud_account: str, project_identifier: str, names: List[str], **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with names in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param names: List of names that should pass the query
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(selected_fips, lambda a: a["name"] in names)

    def search_fips_name_not_in(
        self, cloud_account: str, project_identifier: str, names: List[str], **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with names that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param names: List of names that should not pass the query
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips, lambda a: not a["name"] in names
        )

    def search_fips_name_contains(
        self, cloud_account: str, project_identifier: str, name_snippets: List[str], **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with names containing the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param name_snippets: List of name snippets that should be in the floating ip names returned
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            lambda a: all(name_snippet in a["name"] for name_snippet in name_snippets),
        )

    def search_fips_name_not_contains(
        self, cloud_account: str, project_identifier: str, name_snippets: List[str], **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with names that don't contain the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param name_snippets: List of name snippets that should not be in the floating ip names returned
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            lambda a: all(
                name_snippet not in a["name"] for name_snippet in name_snippets
            ),
        )

    def search_fips_id_in(
        self, cloud_account: str, project_identifier: str, ids: List[str], **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with ids in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param ids: List of ids that should pass the query
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(selected_fips, lambda a: a["id"] in ids)

    def search_fips_id_not_in(
        self, cloud_account: str, project_identifier: str, ids: List[str], **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param ids: List of ids that should not pass the query
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(selected_fips, lambda a: not a["id"] in ids)

    def search_fips_down(
        self, cloud_account: str, project_identifier: str, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips, lambda a: "DOWN" in a["status"]
        )
