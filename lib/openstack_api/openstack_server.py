from typing import List, Dict, Callable, Any

from openstack.compute.v2.server import Server
from openstack.exceptions import HttpException
from openstack_api.dataclasses import (
    NonExistentCheckParams,
    NonExistentProjectCheckParams,
)

from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_query_base import OpenstackQueryBase
from openstack_api.dataclasses import EmailQueryParams
from structs.email_params import EmailParams

from structs.smtp_account import SMTPAccount


class OpenstackServer(OpenstackQueryBase):
    # Lists all possible query presets for server.list
    SEARCH_QUERY_PRESETS: List[str] = [
        "all_servers",
        "servers_older_than",
        "servers_younger_than",
        "servers_last_updated_before",
        "servers_last_updated_after",
        "servers_id_in",
        "servers_id_not_in",
        "servers_name_in",
        "servers_name_not_in",
        "servers_name_contains",
        "servers_name_not_contains",
        "servers_errored",
        "servers_shutoff",
        "servers_errored_and_shutoff",
        "servers_shutoff_before",
    ]

    # Lists possible queries presets that don't require a project to function
    SEARCH_QUERY_PRESETS_NO_PROJECT: List[str] = [
        "servers_older_than",
        "servers_last_updated_before",
        "servers_shutoff_before",
    ]

    # Queries to be used for OpenstackQuery
    def _query_errored(self, server: Server):
        """
        Returns whether a server has error in its status
        """
        return "ERROR" in server["status"]

    def _query_shutoff(self, server: Server):
        """
        Returns whether a server has shutoff in its status
        """
        return "SHUTOFF" in server["status"]

    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(self._connection_cls)

    def _get_query_property_funcs(
        self, cloud_account: str
    ) -> Dict[str, Callable[[Any], Any]]:
        """
        Returns property functions for use with OpenstackQuery.parse_properties
        :param cloud_account: The associated clouds.yaml account
        """
        return {
            "user_email": lambda a: self._query_api.get_user_prop(
                cloud_account, a["user_id"], "email"
            ),
            "user_name": lambda a: self._query_api.get_user_prop(
                cloud_account, a["user_id"], "name"
            ),
        }

    def search_all_servers(
        self, cloud_account: str, project_identifier: str, **_
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
                try:
                    selected_servers.extend(
                        conn.list_servers(
                            filters={
                                "all_tenants": True,
                                "project_id": project.id,
                            }
                        )
                    )
                except HttpException as err:
                    print(f"Failed to list servers in the project with id {project.id}")
                    print(err)
        return selected_servers

    def search_servers_older_than(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[Server]:
        """
        Returns a list of servers older than a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days the servers should be older than
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers, self._query_api.query_datetime_before("created_at", days)
        )

    def search_servers_younger_than(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[Server]:
        """
        Returns a list of servers older than a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days the servers should be older than
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers, self._query_api.query_datetime_after("created_at", days)
        )

    def search_servers_last_updated_before(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[Server]:
        """
        Returns a list of servers updated before a specified number of days in the past
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days before which the servers should have last been updated
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers, self._query_api.query_datetime_before("updated_at", days)
        )

    def search_servers_last_updated_after(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[Server]:
        """
        Returns a list of servers updated after a specified number of days in the past
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days after which the servers should have last been updated
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers, self._query_api.query_datetime_after("updated_at", days)
        )

    def search_servers_name_in(
        self, cloud_account: str, project_identifier: str, names: List[str], **_
    ) -> List[Server]:
        """
        Returns a list of servers with names in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param names: List of names that should pass the query
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers, self._query_api.query_prop_in("name", names)
        )

    def search_servers_name_not_in(
        self, cloud_account: str, project_identifier: str, names: List[str], **_
    ) -> List[Server]:
        """
        Returns a list of servers with names that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param names: List of names that should not pass the query
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers, self._query_api.query_prop_not_in("name", names)
        )

    def search_servers_name_contains(
        self, cloud_account: str, project_identifier: str, name_snippets: List[str], **_
    ) -> List[Server]:
        """
        Returns a list of servers with names containing the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param name_snippets: List of name snippets that should be in the server names returned
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers,
            self._query_api.query_prop_contains("name", name_snippets),
        )

    def search_servers_name_not_contains(
        self, cloud_account: str, project_identifier: str, name_snippets: List[str], **_
    ) -> List[Server]:
        """
        Returns a list of servers with names that don't contain the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param name_snippets: List of name snippets that should not be in the server names returned
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers,
            self._query_api.query_prop_not_contains("name", name_snippets),
        )

    def search_servers_id_in(
        self, cloud_account: str, project_identifier: str, ids: List[str], **_
    ) -> List[Server]:
        """
        Returns a list of servers with ids in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param ids: List of ids that should pass the query
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers,
            self._query_api.query_prop_in("id", ids),
        )

    def search_servers_id_not_in(
        self, cloud_account: str, project_identifier: str, ids: List[str], **_
    ) -> List[Server]:
        """
        Returns a list of servers with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param ids: List of ids that should not pass the query
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_servers, self._query_api.query_prop_not_in("id", ids)
        )

    def search_servers_errored(
        self, cloud_account: str, project_identifier: str, **_
    ) -> List[Server]:
        """
        Returns a list of servers that are in the error state
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(selected_servers, self._query_errored)

    def search_servers_shutoff(
        self, cloud_account: str, project_identifier: str, **_
    ) -> List[Server]:
        """
        Returns a list of servers that are shutoff
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_query(selected_servers, self._query_shutoff)

    def search_servers_errored_and_shutoff(
        self, cloud_account: str, project_identifier: str, **_
    ) -> List[Server]:
        """
        Returns a list of servers that are both errored and shutoff
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_queries(
            selected_servers,
            [self._query_shutoff, self._query_errored],
        )

    def search_servers_shutoff_before(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[Server]:
        """
        Returns a list of servers that are shutoff and were last updated before a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :param days: The number of days before which the servers should have last updated
        :return: A list of servers matching the query
        """
        selected_servers = self.search_all_servers(cloud_account, project_identifier)

        return self._query_api.apply_queries(
            selected_servers,
            [
                self._query_shutoff,
                self._query_api.query_datetime_before("updated_at", days),
            ],
        )

    def find_non_existent_servers(
        self, cloud_account: str, project_identifier: str
    ) -> Dict[str, List[str]]:
        """
        Returns a dictionary containing the ids of projects along with a list of non-existent servers found within them
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :return: A dictionary containing the non-existent server ids and their projects
        """
        return self._query_api.find_non_existent_objects(
            cloud_account=cloud_account,
            project_identifier=project_identifier,
            check_params=NonExistentCheckParams(
                object_list_func=lambda conn, project: conn.list_servers(
                    detailed=False,
                    all_projects=True,
                    bare=True,
                    filters={
                        "all_tenants": True,
                        "project_id": project.id,
                    },
                ),
                object_get_func=lambda conn, object_id: conn.compute.get_server(
                    object_id
                ),
                object_id_param_name="id",
                object_project_param_name="project_id",
            ),
        )

    def find_non_existent_projects(self, cloud_account: str) -> Dict[str, List[str]]:
        """
        Returns a dictionary containing the ids of non-existent projects along with a list of server ids that
        refer to them
        :param cloud_account: The associated clouds.yaml account
        :return: A dictionary containing the non-existent projects and a list of server ids that refer to them
        """
        return self._query_api.find_non_existent_object_projects(
            cloud_account=cloud_account,
            check_params=NonExistentProjectCheckParams(
                object_list_func=lambda conn: conn.list_servers(
                    detailed=False,
                    all_projects=True,
                    bare=True,
                    filters={
                        "all_tenants": True,
                    },
                ),
                object_id_param_name="id",
                object_project_param_name="project_id",
            ),
        )

    # pylint:disable=too-many-arguments
    def email_users(
        self,
        cloud_account: str,
        smtp_account: SMTPAccount,
        project_identifier: str,
        query_preset: str,
        message: str,
        properties_to_select: List[str],
        email_params: EmailParams,
        **kwargs,
    ):
        """
        Finds all servers matching a query and then sends emails to their users
        :param: smtp_account (SMTPAccount): SMTP config
        :param: cloud_account: The account from the clouds configuration to use
        :param: project_identifier: The project this applies to (or empty for all projects)
        :param: query_preset: The query to use when searching for servers
        :param: message: Message to add to the body of emails sent
        :param: properties_to_select: The list of properties to select and output from the found servers
        :param: email_params: See EmailParams
        :param: kwargs: Additional parameters required for the query_preset chosen
        :return:
        """
        query_params = EmailQueryParams(
            required_email_property="user_email",
            valid_search_queries=OpenstackServer.SEARCH_QUERY_PRESETS,
            valid_search_queries_no_project=OpenstackServer.SEARCH_QUERY_PRESETS_NO_PROJECT,
            search_api=self,
            object_type="server",
        )

        return self._query_api.email_users(
            cloud_account=cloud_account,
            smtp_account=smtp_account,
            query_params=query_params,
            project_identifier=project_identifier,
            query_preset=query_preset,
            message=message,
            properties_to_select=properties_to_select,
            email_params=email_params,
            **kwargs,
        )
