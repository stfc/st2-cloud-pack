from typing import Dict, Callable, List

from openstack.compute.v2.server import Server
from tabulate import tabulate

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
        project_identifier: str,
        query_preset: str,
        properties_to_select: List[str],
        group_by: str,
        get_html: bool,
        **kwargs,
    ) -> List[Server]:
        """
        Finds all servers belonging to a project (or all servers if project is empty)
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: The project this applies to (or empty for all servers)
        :param query_preset: The query to use when searching for servers
        :param properties_to_select: The list of properties to select and output from the found servers
        :param group_by: Property to group returned results - can be empty for no grouping
        :param get_html: When True tables returned are in html format
        :return: (String or Dictionary of strings) Table(s) of results grouped by the 'group_by' parameter
        """

        servers = self._server_api[f"search_{query_preset}"](
            cloud_account, project_identifier, **kwargs
        )

        output = self._query_api.parse_and_output_table(
            cloud_account, servers, "server", properties_to_select, group_by, get_html
        )

        return output

    def find_non_existent_servers(self, cloud_account: str, project_identifier: str):
        """
        Returns a dictionary containing the ids of non-existent servers along with the project they are listed in
        This will not necessarily be a complete list as once some are found the query has errored and there
        are no ways to get past it and check for more - however in manual testing it appears these are singular
        and listed at the ends of projects
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :return: A dictionary containing the non-existent server ids and their projects
        """
        server_project_dict = self._server_api.find_non_existent_servers(
            cloud_account=cloud_account, project_identifier=project_identifier
        )

        output = tabulate(server_project_dict.items(), ["Server", "Project"], "grid")
        return output
