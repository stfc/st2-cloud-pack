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

    # pylint:disable=unused-argument,too-many-arguments
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

        property_funcs = OpenstackQuery.get_default_property_funcs(
            "server", cloud_account, self._identity_api
        )
        output = OpenstackQuery.parse_properties(
            servers, properties_to_select, property_funcs
        )

        if group_by != "":
            output = OpenstackQuery.collate_results(output, group_by, get_html)
        else:
            output = OpenstackQuery.generate_table(output, get_html)

        return output
