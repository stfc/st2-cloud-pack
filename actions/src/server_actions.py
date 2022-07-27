from typing import Dict, Callable, List

from openstack.compute.v2.server import Server
from openstack_api.openstack_server import OpenstackServer
from st2common.runners.base_action import Action


class ServerActions(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, config=config, **kwargs)
        self._api: OpenstackServer = config.get("openstack_api", OpenstackServer())

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def server_list(
        self, cloud_account: str, project_identifier: str, **kwargs
    ) -> List[Server]:
        """
        Finds all servers belonging to a project (or all servers if project is empty)
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: The project this applies to (or empty for all servers)
        :return: List of found servers
        """
        return self._api.search_servers(cloud_account, project_identifier)
