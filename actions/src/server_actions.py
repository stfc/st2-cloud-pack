from typing import Dict, Callable, List

from openstack.compute.v2.server import Server
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_server import OpenstackServer
from openstack_api.openstack_query import OpenstackQuery
from st2common.runners.base_action import Action


class ServerActions(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, config=config, **kwargs)
        self._server_api: OpenstackServer = config.get(
            "openstack_api", OpenstackServer()
        )
        self._identity_api: OpenstackIdentity = config.get(
            "openstack_api", OpenstackIdentity()
        )

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    # pylint:disable=unused-argument
    def server_list(
        self, cloud_account: str, project_identifier: str, **kwargs
    ) -> List[Server]:
        """
        Finds all servers belonging to a project (or all servers if project is empty)
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: The project this applies to (or empty for all servers)
        :return: List of found servers
        """
        return self._server_api.search_servers(cloud_account, project_identifier)

    # pylint:disable=unused-argument
    def server_query(
        self,
        cloud_account: str,
        project_identifier: str,
        properties_to_select: List[str],
        **kwargs
    ) -> List[Server]:
        """
        Finds all servers belonging to a project (or all servers if project is empty)
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: The project this applies to (or empty for all servers)
        :param properties_to_select: The list of properties to select and output from the found servers
        :return: List of found servers
        """

        property_funcs = {
            "user_email": lambda a: self._identity_api.find_user_all_domains(
                cloud_account, a["user_id"]
            )["email"],
            "user_name": lambda a: self._identity_api.find_user_all_domains(
                cloud_account, a["user_id"]
            )["name"],
        }

        servers = self._server_api.search_servers(cloud_account, project_identifier)
        output = OpenstackQuery.parse_properties(
            servers, properties_to_select, property_funcs
        )
        output = OpenstackQuery.collate_results(output, "user_email", False)

        return output
