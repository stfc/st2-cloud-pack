from typing import Dict, Callable, List

from openstack.compute.v2.server import Server

from openstack_api.dataclasses import QueryParams
from openstack_api.openstack_server import OpenstackServer
from openstack_api.openstack_query import OpenstackQuery
from st2common.runners.base_action import Action


class ServerActions(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, config=config, **kwargs)
        self._server_api: OpenstackServer = config.get(
            "openstack_server_api", OpenstackServer()
        )
        self._query_api: OpenstackQuery = config.get(
            "openstack_query_api", OpenstackQuery()
        )

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    # pylint:disable=too-many-arguments
    def server_list(
        self,
        cloud_account: str,
        query_preset: str,
        properties_to_select: List[str],
        group_by: str,
        get_html: bool,
        **kwargs,
    ) -> List[Server]:
        """
        Finds all servers belonging to a project (or all servers if project is empty)
        :param cloud_account: The account from the clouds configuration to use
        :param query_preset: The query to use when searching for servers
        :param properties_to_select: The list of properties to select and output from the found servers
        :param group_by: Property to group returned results - can be empty for no grouping
        :param get_html: When True tables returned are in html format
        :return: (String or Dictionary of strings) Table(s) of results grouped by the 'group_by' parameter
        """

        return self._server_api.search(
            cloud_account=cloud_account,
            query_params=QueryParams(
                query_preset=query_preset,
                properties_to_select=properties_to_select,
                group_by=group_by,
                get_html=get_html,
            ),
            **kwargs,
        )

    def find_non_existent_servers(self, cloud_account: str, project_identifier: str):
        """
        Returns a dictionary containing the ids of projects along with a list of non-existent servers found within them
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :return: A dictionary containing the non-existent server ids and their projects
        """
        return self._server_api.find_non_existent_servers(
            cloud_account=cloud_account, project_identifier=project_identifier
        )

    def find_non_existent_projects(self, cloud_account: str):
        """
        Returns a dictionary containing the ids of non-existent projects along with a list of servers that
        refer to them
        :param cloud_account: The associated clouds.yaml account
        :return: A dictionary containing the non-existent server ids and their projects
        """
        return self._server_api.find_non_existent_projects(cloud_account=cloud_account)
